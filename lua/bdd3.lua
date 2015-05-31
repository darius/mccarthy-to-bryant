-- Like bdd2.lua but with an array instead of structs.
-- Now a node ID is an integer index into the array.
-- A constant node is distinguished by its index instead of the rank field.
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

local infinite_rank = 0x7fffffff -- variable rank must be < this
local ranks = {[lit0] = infinite_rank, [lit1] = infinite_rank}
local if0s  = {[lit0] = lit0,          [lit1] = lit1}
local if1s  = {[lit0] = lit0,          [lit1] = lit1}

local function pp(node)  -- XXX
   local shown = {}
   local function show(p)
      assert(p ~= nil)
      if shown[p] == nil then
         shown[p] = true
         if p <= lit1 then
            printf("%d: %d\n", p, p)
         else
            printf("%d: v%d -> %d, %d\n", p, ranks[p], if0s[p], if1s[p])
            show(if0s[p])
            show(if1s[p])
         end
      end
   end
   show(node)
   printf("\n")
end

local function dedup(memo, k1, k2, k3)
   local mem1 = memo[k1]; if mem1 == nil then mem1 = {}; memo[k1] = mem1 end
   local mem2 = mem1[k2]; if mem2 == nil then mem2 = {}; mem1[k2] = mem2 end
   local mem3 = mem2[k3]
   return mem3, mem2
end

local choice_memo = {}

local function build_choice(rank, if0, if1)
   local already, memo_table = dedup(choice_memo, rank, if0, if1)
   if already then return already end

   assert(rank < infinite_rank)
   ranks[#ranks+1] = rank
   if0s[#if0s+1]   = if0
   if1s[#if1s+1]   = if1
   memo_table[if1] = #ranks
   return #ranks
end

local function make_choice(rank, if0, if1)
   if if0 == if1 then return if0 end
   return build_choice(rank, if0, if1)
end

local function evaluate(node, env)
   if node <= lit1 then
      return node
   else
      local value = env[ranks[node]]
      if     value == 0 then return evaluate(if0s[node], env)
      elseif value == 1 then return evaluate(if1s[node], env)
      else assert(false) end
   end
end

local choose

local function do_choose(node, if0, if1)
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
   if     rank <  ranks[node] then return node
   elseif rank == ranks[node] then return do_choose(replacement, if0s[node], if1s[node])
   else                            return make_choice(ranks[node],
                                                      subst(rank, replacement, if0s[node]),
                                                      subst(rank, replacement, if1s[node]))
   end
end

local choose_memo = {}

local function really_choose(node, if0, if1)
   local already, memo_table = dedup(choose_memo, node, if0, if1)
   if already then return already end
   
   assert(lit1 < node)
   local top = math.min(ranks[node], ranks[if0], ranks[if1])
   local on0 = do_choose(subst(top, lit0, node), subst(top, lit0, if0),
                                                 subst(top, lit0, if1))
   local on1 = do_choose(subst(top, lit1, node), subst(top, lit1, if0),
                                                 subst(top, lit1, if1))
   local result = make_choice(top, on0, on1)

   memo_table[if1] = result
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
      local if0 = if0s[node]
      if lit1 < if0 or if0 == goal_node then
         env[ranks[node]] = 0
         node = if0
      else
         env[ranks[node]] = 1
         node = if1s[node]
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
