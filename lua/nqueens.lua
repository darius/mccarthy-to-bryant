local dbg = require 'dbg'
local printf = dbg.printf
local log = dbg.log

local bdd = require 'bdd1'

local function queen(n, qrow, qcol)
   return n*(qrow-1) + qcol
end

local function place_queen(n, qrow, qcol)
   local env = {}

   local function exclude(r, c)
      if 1 <= r and r <= n and 1 <= c and c <= n then
         env[queen(n, r, c)] = 0
      end
   end

   for c = 1, n do exclude(qrow, c) end
   for r = 1, n do exclude(r, qcol) end
   for d = -(n-1), n-1 do
      exclude(qrow+d, qcol+d)
      exclude(qrow+d, qcol-d)
      exclude(qrow-d, qcol+d)
      exclude(qrow-d, qcol-d)
   end
   env[queen(n, qrow, qcol)] = 1
   return bdd.match(env, n*n)
end

local function solve_nqueens(n)
   local result = bdd.lit1
   for row = 1, n do
      local queen_in_row = bdd.lit0
      for col = 1, n do
         queen_in_row = bdd.bdd_or(queen_in_row, place_queen(n, row, col))
      end
      result = bdd.bdd_and(result, queen_in_row)
   end
   return bdd.satisfy_first(result, 1)
end

local function print_board(n, env)
   if env == nil then
      io.write('none\n')
   else
      for row = 1, n do
         for col = 1, n do
            local q = env[queen(n, row, col)]
            if q == 1 then io.write(' Q')
            else           io.write(' .')
            end
         end
         io.write('\n')
      end
   end
   io.write('\n')
end

local function test_nqueens(n)
   print_board(n, solve_nqueens(n))
end

-- pp(lit1)
-- pp(bdd_and(lit0, lit0))
-- pp(bdd_and(lit1, lit0))
-- pp(bdd_and(lit0, lit1))
-- pp(bdd_and(lit1, lit1))

-- pp(place_queen(1, 1, 1))

-- pp(place_queen(2, 1, 1))
-- print_board(2, {1})
-- print_board(2, place_queen(2, 1, 1))

-- print(inspect(satisfy_first(place_queen(2, 2, 2), 1)))

local tmp = place_queen(1, 1, 1)
bdd.pp(tmp)
bdd.pp(tmp.choose(bdd.lit0, tmp))

collectgarbage("collect")
local pre_clock, pre_mem = os.clock(), collectgarbage("count")
test_nqueens(10)
-- choose_memo = {}; collectgarbage("collect")
local post_clock, post_mem = os.clock(), collectgarbage("count")
print(string.format("%.3f seconds, %.3f kb RAM",
                    post_clock - pre_clock, post_mem - pre_mem))
