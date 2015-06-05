-- Like bdd3.lua but with each node struct packed into just one number.
-- TODO clean the code up

local dbg = require 'dbg'
local printf = dbg.printf
local log = dbg.log

local optimize = true

-- index 0 represents the constant 0; index 1 represents the constant 1.
local lit0, lit1 = 0, 1

local function make_constant(value)
   assert(value == 0 or value == 1)
   return value
end

-- XXX maybe better to put rank in the least-significant bits?
local rank_radix    = 0x800           -- 11 bits for rank
local infinite_rank = rank_radix-1    -- variable ranks must be < this
local radix         = 0x200000        -- 21 bits each for if0, if1
assert(radix <= 0x200000) -- see pack_hash_key

local function pack(rank, if0, if1)
   assert(0 <= rank and rank < rank_radix)
   assert(0 <= if0 and if0 < radix)
   return radix * ((radix * rank) + if0) + if1
end

local function unpack(val)
   local if1 = val % radix;          assert(0 <= if1)
   val = (val - if1) / radix
   local if0 = val % radix;          assert(0 <= if0)
   local rank = (val - if0) / radix; assert(0 <= rank and rank < rank_radix)
   return rank, if0, if1
end

-- Take three node IDs (each in range [0..radix))
-- and return a double-precision floating-point number
-- uniquely determined by them. Since a node ID takes 21
-- bits, we need to cram 63 together in total.
local function pack_hash_key(x, y, z)
   -- An IEEE double has 52 bits mantissa, 11 bits exponent:
   local yz = radix*y + z           -- 42 bits
   local x1 = x % 0x400             -- 10 bits
   local exponent = (x-x1) / 0x400  -- 11 bits
   local mantissa = (yz * 0x400) + x1
   return math.ldexp(mantissa, exponent - 1023)  -- XXX I'm not sure about this
end

local nodes = {[lit0] = pack(infinite_rank, lit0, lit0),
               [lit1] = pack(infinite_rank, lit1, lit1)}

local function pp(node)  -- XXX
   local shown = {}
   local function show(p)
      assert(p ~= nil)
      if shown[p] == nil then
         shown[p] = true
         if p <= lit1 then
            printf("%d: %d\n", p, p)
         else
            local rank, if0, if1 = unpack(nodes[p])
            printf("%d: v%d -> %d, %d\n", p, rank, if0, if1)
            show(if0)
            show(if1)
         end
      end
   end
   show(node)
   printf("\n")
end

local choice_memo = {}

local function build_choice(rank, if0, if1)
   local key = pack(rank, if0, if1)
   local already = choice_memo[key]
   if already ~= nil then return already end

   nodes[#nodes+1] = key
   choice_memo[key] = #nodes
   return #nodes
end

local function make_choice(rank, if0, if1)
   if if0 == if1 then return if0 end
   return build_choice(rank, if0, if1)
end

local function evaluate(node, env)
   if node <= lit1 then
      return node
   else
      local rank, if0, if1 = unpack(nodes[node])
      local value = env[rank]
      if     value == 0 then return evaluate(if0, env)
      elseif value == 1 then return evaluate(if1, env)
      else assert(false) end
   end
end

local choose

local function do_choose(node, if0, if1)
   assert(node ~= nil)
   if node <= lit1 then
      if     node == lit0 then return if0
      elseif node == lit1 then return if1
      else assert(false)
      end
   else
      if optimize then
         if if0 == if1 then return if0 end
         if if0 == lit0 and if1 == lit1 then return node end
      end
      return choose(node, if0, if1)
   end
end

local function subst(rank, replacement, node)
   assert(node ~= nil)
   assert(replacement ~= nil)
   local node_rank, if0, if1 = unpack(nodes[node])
   if     rank <  node_rank then return node
   elseif rank == node_rank then return do_choose(replacement, if0, if1)
   else                          return make_choice(node_rank,
                                                    subst(rank, replacement, if0),
                                                    subst(rank, replacement, if1))
   end
end

local choose_memo = {}

local function really_choose(node, if0, if1)
   local key = pack_hash_key(node, if0, if1)
   local already = choose_memo[key]
   if already ~= nil then return already end
   
   assert(lit1 < node)
   local node_rank, node_if0, node_if1 = unpack(nodes[node])
   local if0_rank = unpack(nodes[if0])
   local if1_rank = unpack(nodes[if1])

   local top = math.min(node_rank, if0_rank, if1_rank)
   local on0 = do_choose(subst(top, lit0, node), subst(top, lit0, if0),
                                                 subst(top, lit0, if1))
   local on1 = do_choose(subst(top, lit1, node), subst(top, lit1, if0),
                                                 subst(top, lit1, if1))
   local result = make_choice(top, on0, on1)

   choose_memo[key] = result
   return result
end

choose = really_choose

-- Return the lexicographically first env such that
-- node.evaluate(env) == goal, if there's any; else nil.
-- The env may have nils for variables that don't matter.
local function satisfy_first(node, goal)
   local goal_node = make_constant(goal)
   local env = {}
   while lit1 < node do
      local rank, if0, if1 = unpack(nodes[node])
      if lit1 < if0 or if0 == goal_node then
         env[rank], node = 0, if0
      else
         env[rank], node = 1, if1
      end
   end
   if node ~= goal_node then return nil end
   return env
end

local function bdd_and(node1, node2) return do_choose(node2, lit0, node1) end
local function bdd_or (node1, node2) return do_choose(node2, node1, lit1) end

-- Return a node that's true just when env's vars have their given values.
local function match(env, max_rank)
   local node = lit1
   for rank = max_rank, 1, -1 do
      if     env[rank] == nil then 
      elseif env[rank] == 0   then node = make_choice(rank, node, lit0)
      elseif env[rank] == 1   then node = make_choice(rank, lit0, node)
      else assert(false) end
   end
   return node
end

local function make_variable(rank)
   return build_choice(rank, lit0, lit1)
end

local function clear_choose_memos()
   for k in pairs(choose_memo) do
      choose_memo[k] = nil
   end
end

return {
   lit0 = lit0,
   lit1 = lit1,
   make_constant = make_constant,
   make_variable = make_variable,
   subst = subst,
   satisfy_first = satisfy_first,
   bdd_and = bdd_and,
   bdd_or = bdd_or,
   match = match,
   pp = pp,
   choose = do_choose,
   clear_choose_memos = clear_choose_memos,
}
