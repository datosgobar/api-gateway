return {
  no_consumer = true, -- this plugin will only be API-wide,
  fields = {
    endpoint = {type = "string", required = true},
    token = {type = "string", required = true},
    host = {type = "host", required = false},
    api_data = {type = "string", required = false},
    -- Describe your plugin's configuration's schema here.
  },
  self_check = function(schema, plugin_t, dao, is_updating)
    -- perform any custom verification
    return true
  end
}
