const express = require('express')
const app = express()
const port = 5000

app.use(express.json());


battleToken = 0

app.post('/api/events/OnBattleStart', (req, res) => {
    console.log(req.body);
    console.log("Send new token: " + battleToken);
    res.send(`${battleToken++}`).end()

    console.log('_____________________________\n\n');
})

app.post('/api/events/send', (req, res) => {
    req.body.events.forEach(event => {
        console.log('EventName: ' + event.EventName);
        console.log('Token: ' + event.Token);
        console.log(event)
        console.log('_____________________________\n\n');
    });

    res.status(200).end()
})


app.get('/', (req, res) => {
    res.send('Work fine')
})

app.listen(port, () => {
    console.log(`Server placeholder start at http://localhost:${port}`)
})