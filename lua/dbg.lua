DEBUG = false

local function printf(...)
   io.write(string.format(...))
end

local function log(...)
   if DEBUG then printf(...) end
end

return {
   printf = printf,
   log = log,
}
