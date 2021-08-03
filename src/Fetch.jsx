import React, { useState, useEffect } from "react";
import axios from "axios";
import "./Fetch.css";
import Modal from "react-modal";
import Loader from "react-loader-spinner";
import { Recorder } from "react-voice-recorder";
import "react-voice-recorder/dist/index.css";

const customStyles = {
  content: {
    top: "50%",
    left: "50%",
    right: "auto",
    bottom: "auto",
    marginRight: "-50%",
    transform: "translate(-50%, -50%)",
    borderRadius: "10px",
    height: "200px",
    backgroundColor: "rgb(19 19 19)",
  },
};

Modal.setAppElement("#root");

const Fetch = () => {
  const [file, setFile] = useState({ voice_file: "" });
  const [data, setData] = useState(null);
  const [error, setError] = useState(false);
  const [modalIsOpen, setmodalIsOpen] = useState(false);

  const handleFile = (e) => {
    const fileItem = e.target.files[0];
    console.log("fileItem", fileItem);
    setFile(fileItem);
    setError(false);
  };

  const handleUpload = (e) => {
    setmodalIsOpen(true);

    const formdata = new FormData();
    formdata.append("voice_file", file);

    axios({
      url: "https://parkinsonspredictionmodel-api.herokuapp.com/predict",
      method: "POST",
      data: formdata,
    })
      .then((res) => {
        setData(res.data);
        //    setmodalIsOpen(true)
      })
      .catch((err) => {
        setError(true);
      });
  };

  const closeModal = () => {
    setmodalIsOpen(false);
  };

  return (
    <div className="container">
      <h1 style={{ letterSpacing: "2px" }}>Parkinson's Disease Predictor</h1>
      <div className="formcontainer">
        <form>
          <div className="input">
            <label className="selectFile">
              Submit an audio clip (.wav file)
            </label>
            <label class="custom-file-upload">
              Choose a file
              <input type="file" name="file" onChange={handleFile} />
            </label>
          </div>

          <div className="upload">
            <a className="uploadBtn" onClick={handleUpload}>
              Upload
            </a>
          </div>
        </form>
      </div>

      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        style={customStyles}
      >
        <div></div>

        <p style={{ color: "white" }} className="prediction">
          Analyzing...{" "}
        </p>
        {error ? (
          <p style={{ color: "white" }} className="predictionVal">
            There is no data or Incorrect audio file choosen
          </p>
        ) : data == null ? (
          <Loader type="Puff" color="#00BFFF" height={100} width={100} />
        ) : (
          <p style={{ color: "white" }} className="predictionVal">
            {data}
          </p>
        )}
      </Modal>
    </div>
  );
};

export default Fetch;
