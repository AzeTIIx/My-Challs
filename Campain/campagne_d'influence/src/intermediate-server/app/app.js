const express = require('express');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const app = express();

app.use(express.static('public'));

app.use((req, res, next) => {
  res.setHeader('Access-Control-Allow-Origin', '*'); 
  res.setHeader('Access-Control-Allow-Methods', 'GET'); 
  next();
});

const mediaDir = path.join(__dirname, 'tempmedia');
if (!fs.existsSync(mediaDir)) {
    console.error(`Le répertoire ${mediaDir} n'existe pas.`);
    process.exit(1);
}
app.use('/media', express.static(mediaDir));

app.get('/latest-media', (req, res) => {
    fs.readdir(mediaDir, (err, files) => {
        if (err) {
            console.error('Erreur lors de la lecture du répertoire média :', err);
            return res.status(500).send('Erreur lors de la lecture du répertoire média');
        }
        const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif','.mp4'];
        const mediaFiles = files.filter(file => imageExtensions.includes(path.extname(file).toLowerCase())).sort().reverse();
        if (mediaFiles.length > 0) {
            const latestMediaPath = path.join(mediaDir, mediaFiles[0]);
            res.sendFile(latestMediaPath);
        } else {
            res.status(404).send('Aucun média trouvé');
        }
    });
});


app.get('/ping', (req, res) => {
  const ip = req.query.ip;  
  exec(`ping -c 4 ${ip}`, (error, stdout, stderr) => {
    if (error) {
      return res.status(500).json({ error: stderr });
    }
    res.json({ message: stdout });
  });
});

app.listen(3000, () => console.log('Intermediate server running on port 3000'));
