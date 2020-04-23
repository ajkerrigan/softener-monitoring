# softener-monitoring

Monitor power usage for my water softener, alert when it cycles. This is mostly notes and tinkering.

### Components

Hardware:

* Water Softener
* TP-Link HS110 WiFi Smart Plug

Software:

* InfluxDB: Holds power consumption time series data.
* https://github.com/plasticrake/tplink-smarthome-api: Lets us scrape energy metrics from the HS110 plug. The included Kasa app doesn't provide enough granularity to identify when a water softener cycles. We need more granularity and flexibility in reporting.
* Flask: Run a small API that can receive InfluxDB alerts and send email notifications via SendGrid.

### Deploying

* Run InfluxDB on its own, set up:
  * Org and bucket
  * Access token with permission to write to a bucket
* Create config and secret entries referenced in docker-compose.yml
* `docker stack deploy -c docker-compose.yml softener`
* In InfluxDB, set up:
  * Monitoring dashboard
  * Threshold and Deadman Checks
  * Notification endpoint targeting the Flask endpoint
  * Alerting rules based on power metrics:
    * Ok (Idle): 700mW - 1W
	* Info (Running): >1W
	* Warn (Low Draw): <700mW
	* Crit: From deadman check
