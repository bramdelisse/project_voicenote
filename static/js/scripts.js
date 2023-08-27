// code copied with love from https://medium.com/jeremy-gottfrieds-tech-blog/javascript-tutorial-record-audio-and-encode-it-to-mp3-2eedcd466e78
// and from https://stackoverflow.com/questions/71268311/how-to-convert-blob-to-wav-file-in-javascript-and-connect-python-flask

navigator.mediaDevices.getUserMedia({audio:true})
.then(stream => {handlerFunction(stream)})


function handlerFunction(stream) {
  rec = new MediaRecorder(stream);
  rec.ondataavailable = e => {
    audioChunks.push(e.data);
    if (rec.state == "inactive"){
      let blob = new Blob(audioChunks,{type:'audio/mpeg-3'});
      recordedAudio.src = URL.createObjectURL(blob);
      alert(`object url created locally ${recordedAudio.src}`)
      recordedAudio.controls=true;
      recordedAudio.autoplay=true;
    }
  }
}
          

record.onclick = e => {
  console.log('Record was clicked')
  record.disabled = true;
  record.style.backgroundColor = "blue"
  stopRecord.disabled=false;
  audioChunks = [];
  rec.start();
}
stopRecord.onclick = e => {
  console.log("Stop was clicked")
  record.disabled = false;
  stop.disabled=true;
  record.style.backgroundColor = "red"
  rec.stop();
}
sendRecording.onclick = e => {
  console.log("Upload recording was clicked")
  let formData = new FormData();
  formData.append('data', blob);
  console.log('blob', blob)
  console.log(formData)
  
  // var xhr = new XMLHttpRequest();
  // xhr.open('POST', '/upload', true);
  // xhr.send(blob);
  // console.log("function sendData triggered")

  $.ajax({
    type: 'POST',
    url: '/upload',
    data: formData,
    contentType: false,
    processData: false,
    success: function(result) {
      console.log('success', result);

      $("#chatbox").append(`<p class ="userText"><audio style="background-color:white;" controls> <source src="${Url}" type="audio/wav"></audio></p>`);
      $("#chatbox").append(`<p class ="botText"><span>${result.emotion}</span></p>`);
      $("#textInput").val("")
    },
    error: function(result) {
      alert('sorry an error occured');
    }
  }).done(function(data) {
    console.log(data);
  });

  // fetch('./upload', {method:"POST", body: blob}).then(response => console.log(response.text()))

}

  // function sendData() {
  //   blob = recordedAudio.src
  //   var xhr = new XMLHttpRequest();
  //   xhr.open('POST', '/upload', true);
  //   xhr.send(blob);
  //   console.log("function sendData triggered")
  //   }