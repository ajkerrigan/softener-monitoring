const dockerSecrets = require('docker-swarm-secrets');
const secrets = dockerSecrets.readSecretsSync();
const config = dockerSecrets.readSecretsSync({
    encoding: 'utf-8',
    secretsDir: '/run/config',
    debug: true
});

const tplink = require('tplink-smarthome-api');
const tpclient = new tplink.Client();

const {InfluxDB} = require('@influxdata/influxdb-client')
const influxDB = new InfluxDB({
    url: config.influxdb_url,
    token: secrets.influxdb_token
})
const writeApi = influxDB.getWriteApi(config.influxdb_org, config.influxdb_bucket)

function post_metrics() {
    let sysinfo, emeter;
    tpclient.getDevice({host: config.plug_host}).then((plug)=>{
        plug.getSysInfo().then((data) => { sysinfo = data });
        plug.emeter.getRealtime().then((data) => {
            let postdata = `emeter,device=softener power=${data.power},current=${data.current},voltage=${data.voltage} ${Math.floor(new Date())}000000`
            writeApi.writeRecord(postdata)
            writeApi.flush().catch((err) => {
                console.error(`Shit broke: ${err}`)
            });
        });
    });
}

setInterval(post_metrics, 5000)
