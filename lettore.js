

//api.genius.com/search?q=Kendrick%20Lamar%2C%20LOVE = Kendrick Lamar, LOVE
//RSD-yB6x3Z3YLTBqZtBMoYR8xnJi5MT2xfULe2Jthi9KetZeAwyOZldpu6FNe4pT

const https = require('https');
  
  
var options = {
  url: 'https://api.genius.com/search?q=Kendrick%20Lamar%2C%20LOVE',
  method: 'POST',
  headers: {
    'User-Agent': 'my request',
    //'Authorization': 'Bearer RSD-yB6x3Z3YLTBqZtBMoYR8xnJi5MT2xfULe2Jthi9KetZeAwyOZldpu6FNe4pT',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
};




const request = https.request(options, (response) => {
    let data = '';
    response.on('data', (chunk) => {
        data = data + chunk.toString();
    });
  
    response.on('end', () => {
        const body = JSON.parse(data);
        console.log(body);
    });
})
  
request.on('error', (error) => {
    console.log('An error', error);
});
  
request.end() 