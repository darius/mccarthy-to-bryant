-- Like bdd1.lua but with structs instead of objects.
-- TODO clean the code up

local dbg = require 'dbg'
local printf = dbg.printf
local log = dbg.log

local optimize = true

local infinity = 1/0

local function pp(node)
   local c, memo = 0, {}
   local function walk(p)
      local id = memo[p]
      if id == nil then
         id = c; c = c + 1
         memo[p] = id
         if p.rank < infinity then
            walk(p.if0)
            walk(p.if1)
         end
      end
   end
   walk(node)
   local shown = {}
   local function show(p)
      if shown[p] == nil then
         shown[p] = true
         if p.rank < infinity then
            printf("%d: v%d -> %d, %d\n", memo[p], p.rank, memo[p.if0], memo[p.if1])
            show(p.if0)
            show(p.if1)
         else
            printf("%d: %d\n", memo[p], p.value)
         end
      end
   end
   show(node)
   printf("\n")
end

local function build_constant(value)
   return {
      rank = infinity,
      value = value,
   }
end

local lit0, lit1 = build_constant(0), build_constant(1)

local function make_constant(value)
   if     value == 0 then return lit0
   elseif value == 1 then return lit1
   else assert(false) end
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
   if already then
      return already
   end
   local node = {
      rank = rank,
      if0 = if0,
      if1 = if1,
   }
   memo_table[if1] = node
   return node
end

local function make_choice(rank, if0, if1)
   if if0 == if1 then return if0 end
   return build_choice(rank, if0, if1)
end

local function evaluate(node, env)
   if node.rank == infinity then
      return value
   else
      local value = env[node.rank]
      if     value == 0 then return evaluate(node.if0, env)
      elseif value == 1 then return evaluate(node.if1, env)
      else assert(false) end
   end
end

local choose

local function do_choose(node, if0, if1)
   if node.rank == infinity then
      if     node.value == 0 then return if0
      elseif node.value == 1 then return if1
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
   local result
   if     rank <  node.rank then return node
   elseif rank == node.rank then return do_choose(replacement, node.if0, node.if1)
   else                          return make_choice(node.rank,
                                                    subst(rank, replacement, node.if0),
                                                    subst(rank, replacement, node.if1))
   end
end

local choose_memo = {}

local function really_choose(node, if0, if1)
   local already, memo_table = dedup(choose_memo, node, if0, if1)
   if already then return already end
   
   assert(node.rank < infinity)
   local top = math.min(node.rank, if0.rank, if1.rank)
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
   local env = {}
   while node.rank ~= infinity do
      local if0 = node.if0
      if if0.rank < infinity or if0.value == goal then
         env[node.rank] = 0
         node = if0
      else
         env[node.rank] = 1
         node = node.if1
      end
   end
   if node.value ~= goal then return nil end
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
