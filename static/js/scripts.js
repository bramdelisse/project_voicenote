// code copied with love from https://medium.com/jeremy-gottfrieds-tech-blog/javascript-tutorial-record-audio-and-encode-it-to-mp3-2eedcd466e78
// and from https://stackoverflow.com/questions/71268311/how-to-convert-blob-to-wav-file-in-javascript-and-connect-python-flask

let rec, audioChunks = [], blob;

document.addEventListener("DOMContentLoaded", function(){
  navigator.mediaDevices.getUserMedia({audio:true})
  .then(stream => {handlerFunction(stream)})

  const recordedAudio = document.getElementById("recordedAudio");
  const record = document.getElementById("record");
  const stopRecord = document.getElementById("stopRecord");
  const sendRecording = document.getElementById("sendRecording");

  navigator.mediaDevices.getUserMedia({audio:true})
  .then(stream => {handlerFunction(stream)})

  let blob;

  function handlerFunction(stream) {
    rec = new MediaRecorder(stream);
    rec.ondataavailable = e => {
      audioChunks.push(e.data);
      if (rec.state == "inactive"){
        blob = new Blob(audioChunks, { type: "audio/mp3; codecs=opus" });
        recordedAudio.src = URL.createObjectURL(blob);
        console.log(`object url created locally ${recordedAudio.src}`)
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
    formData.append('file', blob, "blob.mp3");
    fetch('./upload', {method:"POST", body: formData}).then(response => console.log(response))
  }
});