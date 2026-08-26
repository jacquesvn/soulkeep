-- WoWRosterExport: snapshots per-character data the REST API can't serve
-- (gold, Great Vault, currencies, lockouts) into SavedVariables for the
-- WoW Roster desktop app. Data writes to disk on logout or /reload.
local f = CreateFrame("Frame")
f:RegisterEvent("PLAYER_ENTERING_WORLD")
f:RegisterEvent("PLAYER_LOGOUT")

local function collect()
  WoWRosterExportDB = WoWRosterExportDB or {}
  local name, realm = UnitName("player"), GetRealmName()
  if not name or not realm then return end
  local d = { ts = time(), gold = GetMoney(), level = UnitLevel("player") }

  local ok, ilvl = pcall(function() return select(2, GetAverageItemLevel()) end)
  if ok and ilvl then d.ilvl = math.floor(ilvl + 0.5) end

  d.vault = {}
  if C_WeeklyRewards and C_WeeklyRewards.GetActivities then
    local ok2, acts = pcall(C_WeeklyRewards.GetActivities)
    if ok2 and type(acts) == "table" then
      for _, a in ipairs(acts) do
        table.insert(d.vault, { type = a.type, index = a.index,
                                progress = a.progress, threshold = a.threshold, level = a.level })
      end
    end
  end

  d.currencies = {}
  if C_CurrencyInfo and C_CurrencyInfo.GetCurrencyListSize then
    for i = 1, C_CurrencyInfo.GetCurrencyListSize() do
      local ok3, info = pcall(C_CurrencyInfo.GetCurrencyListInfo, i)
      if ok3 and info and not info.isHeader and (info.quantity or 0) > 0 then
        table.insert(d.currencies, { name = info.name, qty = info.quantity })
      end
    end
  end

  d.lockouts = {}
  if GetNumSavedInstances then
    for i = 1, GetNumSavedInstances() do
      local iname, _, reset, _, locked, _, _, _, _, diffName, numEnc, encProg = GetSavedInstanceInfo(i)
      if locked then
        table.insert(d.lockouts, { name = iname, diff = diffName, done = encProg, total = numEnc, reset = reset })
      end
    end
  end

  WoWRosterExportDB[name .. "-" .. realm] = d
end

f:SetScript("OnEvent", function(_, ev)
  if ev == "PLAYER_ENTERING_WORLD" then
    C_Timer.After(10, function() pcall(collect) end)   -- let vault/currency data load in
  else
    pcall(collect)
  end
end)

SLASH_WOWROSTER1 = "/wowroster"
SlashCmdList["WOWROSTER"] = function()
  pcall(collect)
  print("|cffb15cffWoW Roster|r: snapshot taken — it writes to disk on logout or /reload.")
end
