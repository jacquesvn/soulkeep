-- WoWRosterExport: snapshots per-character data the REST API can't serve
-- (gold, Great Vault, currencies, lockouts, keystone, bags, /played) into
-- SavedVariables for the WoW Roster desktop app. Writes to disk on logout or /reload.
local f = CreateFrame("Frame")
f:RegisterEvent("PLAYER_ENTERING_WORLD")
f:RegisterEvent("PLAYER_LOGOUT")
f:RegisterEvent("TIME_PLAYED_MSG")

-- /played capture: request quietly, cache the reply, embed it in every snapshot
local pendingPlayed = nil
local function requestPlayed()
  if not RequestTimePlayed then return end
  local orig = ChatFrame_DisplayTimePlayed
  if orig then ChatFrame_DisplayTimePlayed = function() end end
  RequestTimePlayed()
  if orig then C_Timer.After(1.5, function() ChatFrame_DisplayTimePlayed = orig end) end
end

local function collect()
  WoWRosterExportDB = WoWRosterExportDB or {}
  local name, realm = UnitName("player"), GetRealmName()
  if not name or not realm then return end
  local d = { ts = time(), gold = GetMoney(), level = UnitLevel("player") }
  if pendingPlayed then d.played = pendingPlayed end

  local ok, ilvl = pcall(function() return select(2, GetAverageItemLevel()) end)
  if ok and ilvl then d.ilvl = math.floor(ilvl + 0.5) end

  d.vault = {}
  if C_WeeklyRewards and C_WeeklyRewards.GetActivities then
    local ok2, acts = pcall(C_WeeklyRewards.GetActivities)
    if ok2 and type(acts) == "table" then
      for _, a in ipairs(acts) do
        local v = { type = a.type, index = a.index,
                    progress = a.progress, threshold = a.threshold, level = a.level }
        -- reward preview: what the vault is actually offering, once generated
        if a.rewards and #a.rewards > 0 and C_WeeklyRewards.GetItemHyperlink then
          local okh, link = pcall(C_WeeklyRewards.GetItemHyperlink, a.rewards[1].itemDBID)
          if okh and link and C_Item and C_Item.GetDetailedItemLevelInfo then
            local oki, rilvl = pcall(C_Item.GetDetailedItemLevelInfo, link)
            if oki and rilvl and rilvl > 0 then v.reward = rilvl end
          end
        end
        table.insert(d.vault, v)
      end
    end
    if C_WeeklyRewards.HasAvailableRewards then
      local okr, avail = pcall(C_WeeklyRewards.HasAvailableRewards)
      if okr and avail then d.vault_ready = true end
    end
  end

  d.currencies = {}
  if C_CurrencyInfo and C_CurrencyInfo.GetCurrencyListSize then
    for i = 1, C_CurrencyInfo.GetCurrencyListSize() do
      local ok3, info = pcall(C_CurrencyInfo.GetCurrencyListInfo, i)
      if ok3 and info and not info.isHeader and (info.quantity or 0) > 0 then
        local cur = { name = info.name, qty = info.quantity }
        if (info.maxQuantity or 0) > 0 then cur.cap = info.maxQuantity end
        if (info.maxWeeklyQuantity or 0) > 0 then
          cur.wk = info.quantityEarnedThisWeek or 0
          cur.wkmax = info.maxWeeklyQuantity
        end
        table.insert(d.currencies, cur)
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

  -- keystone in bag: which key this soul holds
  if C_MythicPlus and C_MythicPlus.GetOwnedKeystoneLevel then
    local ok4, lvl = pcall(C_MythicPlus.GetOwnedKeystoneLevel)
    local ok5, mapID = pcall(C_MythicPlus.GetOwnedKeystoneChallengeMapID)
    if ok4 and ok5 and lvl and mapID then
      local mname
      if C_ChallengeMode and C_ChallengeMode.GetMapUIInfo then
        local okn, nm = pcall(C_ChallengeMode.GetMapUIInfo, mapID)
        if okn then mname = nm end
      end
      d.keystone = { map = mname or ("map " .. mapID), level = lvl }
    end
  end

  -- bags: everything this soul carries (aggregated by item)
  if C_Container and C_Container.GetContainerNumSlots then
    local agg = {}
    for bagID = 0, 5 do
      local slots = C_Container.GetContainerNumSlots(bagID) or 0
      for slot = 1, slots do
        local ok6, info = pcall(C_Container.GetContainerItemInfo, bagID, slot)
        if ok6 and info and info.itemID and (info.stackCount or 0) > 0 then
          local e = agg[info.itemID]
          if e then
            e.q = e.q + info.stackCount
          else
            local iname = info.itemName
            if not iname and C_Item and C_Item.GetItemNameByID then
              local okn2, nm2 = pcall(C_Item.GetItemNameByID, info.itemID)
              if okn2 then iname = nm2 end
            end
            agg[info.itemID] = { i = info.itemID, q = info.stackCount, n = iname }
          end
        end
      end
    end
    d.bag = {}
    for _, e in pairs(agg) do table.insert(d.bag, e) end
  end

  -- never let an early-login snapshot (data not loaded yet) clobber good values with zeros
  local prior = WoWRosterExportDB[name .. "-" .. realm]
  if prior then
    if prior.played and not d.played then d.played = prior.played end
    if (d.gold or 0) == 0 and (prior.gold or 0) > 0 then d.gold = prior.gold end
    if (d.ilvl or 0) == 0 and (prior.ilvl or 0) > 0 then d.ilvl = prior.ilvl end
    if #d.currencies == 0 and prior.currencies and #prior.currencies > 0 then d.currencies = prior.currencies end
    if #d.vault == 0 and prior.vault and #prior.vault > 0 then d.vault = prior.vault end
    if (not d.bag or #d.bag == 0) and prior.bag and #prior.bag > 0 then d.bag = prior.bag end
  end
  WoWRosterExportDB[name .. "-" .. realm] = d
end

f:SetScript("OnEvent", function(_, ev, arg1)
  if ev == "TIME_PLAYED_MSG" then
    if arg1 and arg1 > 0 then
      pendingPlayed = arg1
      local key = UnitName("player") .. "-" .. GetRealmName()
      if WoWRosterExportDB and WoWRosterExportDB[key] then
        WoWRosterExportDB[key].played = arg1
      end
    end
    return
  end
  if ev == "PLAYER_ENTERING_WORLD" then
    C_Timer.After(2, function() pcall(requestPlayed) end)  -- reply is cached; any later snapshot embeds it
    C_Timer.After(10, function() pcall(collect) end)   -- let vault/currency data load in
    C_Timer.After(45, function() if not pendingPlayed then pcall(requestPlayed) end end)
    C_Timer.After(60, function() pcall(collect) end)   -- and once more when fully settled
  else
    pcall(collect)
  end
end)

SLASH_WOWROSTER1 = "/wowroster"
SlashCmdList["WOWROSTER"] = function()
  pcall(requestPlayed)
  pcall(collect)
  print("|cffb15cffWoW Roster|r: snapshot taken — it writes to disk on logout or /reload.")
end
