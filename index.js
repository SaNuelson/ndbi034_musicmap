const express = require("express");
const fileUpload = require("express-fileupload");
const cors = require('cors');
const path = require('path');
const app = express();

app.use(fileUpload({
  createParentPath: true
}));

app.use(cors());

const port = process.env.PORT || 3000;

app.listen(port, () => 
  console.log(`App is listening on port ${port}.`)
);

app.get("/", (req, res) => {
  console.log(req.query);
  res.sendFile(path.resolve(__dirname, "./views/index.html"));
});

app.post('/upload', async (req, res) => {
  console.log("Upload request came...", req.files);
  try {
      if(!req.files) {
          res.send({
              status: false,
              message: 'No file uploaded'
          });
      } else {
          //Use the name of the input field (i.e. "avatar") to retrieve the uploaded file
          let sound = req.files.sound;
          
          //Use the mv() method to place the file in upload directory (i.e. "uploads")
          sound.mv('./uploads/' + sound.name);

          //send response
          res.send({
              status: true,
              message: 'File is uploaded',
              data: {
                  name: sound.name,
                  mimetype: sound.mimetype,
                  size: sound.size
              }
          });
      }
  } catch (err) {
      res.status(500).send(err);
  }
});