from flask import Flask, render_template
from flask import request
import flask
from pycaret.classification import *
import os
from flask_cors import CORS, cross_origin
import parselmouth
from parselmouth.praat import call

def measurePitch(voiceID, f0min, f0max, unit):
    sound = parselmouth.Sound(voiceID) # read the sound
    pitch = call(sound, "To Pitch", 0.0, f0min, f0max)
    pointProcess = call(sound, "To PointProcess (periodic, cc)", f0min, f0max)
    localJitter = call(pointProcess, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)
    localabsoluteJitter = call(pointProcess, "Get jitter (local, absolute)", 0, 0, 0.0001, 0.02, 1.3)
    rapJitter = call(pointProcess, "Get jitter (rap)", 0, 0, 0.0001, 0.02, 1.3)
    ppq5Jitter = call(pointProcess, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3)
    localShimmer =  call([sound, pointProcess], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    localdbShimmer = call([sound, pointProcess], "Get shimmer (local_dB)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    apq3Shimmer = call([sound, pointProcess], "Get shimmer (apq3)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    aqpq5Shimmer = call([sound, pointProcess], "Get shimmer (apq5)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    apq11Shimmer =  call([sound, pointProcess], "Get shimmer (apq11)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
    harmonicity05 = call(sound, "To Harmonicity (cc)", 0.01, 500, 0.1, 1.0)
    hnr05 = call(harmonicity05, "Get mean", 0, 0)
    harmonicity15 = call(sound, "To Harmonicity (cc)", 0.01, 1500, 0.1, 1.0)
    hnr15 = call(harmonicity15, "Get mean", 0, 0)
    harmonicity25 = call(sound, "To Harmonicity (cc)", 0.01, 2500, 0.1, 1.0)
    hnr25 = call(harmonicity25, "Get mean", 0, 0)
    harmonicity35 = call(sound, "To Harmonicity (cc)", 0.01, 3500, 0.1, 1.0)
    hnr35 = call(harmonicity35, "Get mean", 0, 0)
    harmonicity38 = call(sound, "To Harmonicity (cc)", 0.01, 3800, 0.1, 1.0)
    hnr38 = call(harmonicity38, "Get mean", 0, 0)
    return localJitter, localabsoluteJitter, rapJitter, ppq5Jitter, localShimmer, localdbShimmer, apq3Shimmer, aqpq5Shimmer, apq11Shimmer, hnr05, hnr15 ,hnr25 ,hnr35 ,hnr38

app = flask.Flask(__name__)
model = load_model('trained_model')
cols = ['Jitter', 'Jitter_absolute', 'Jitter-rap', 'Jitter_ppq5', 'Shimmer',
       'Shimmer_db', 'Shimmer_apq3', 'Shimmeraqpq5', 'Shimmer_apq11', 'hnr05',
       'hnr15', 'hnr25', 'hnr35', 'hnr38']
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return "Parkinsons_Model"
    # return render_template('index.html')


@app.route('/predict',methods=['POST'])
@cross_origin(origin='*')
def predict():
    voiceData = request.files['voice_file']
    voiceData.save(voiceData.filename)

    cwd = os.getcwd()
    print(cwd+"/"+voiceData.filename)
    # filename = glob(cwd+"/"+voiceData.filename)
    # print(filename)
    sound = parselmouth.Sound(cwd+"/"+voiceData.filename)
    (localJitter, localabsoluteJitter, rapJitter, ppq5Jitter, localShimmer, localdbShimmer, apq3Shimmer,aqpq5Shimmer,apq11Shimmer, hnr05, hnr15, hnr25, hnr35, hnr38) = measurePitch(sound, 75, 1000, "Hertz")

    input_values = []
    input_values.append(localJitter)
    input_values.append(localabsoluteJitter)
    input_values.append(rapJitter)
    input_values.append(ppq5Jitter)
    input_values.append(localShimmer)
    input_values.append(localdbShimmer)
    input_values.append(apq3Shimmer)
    input_values.append(aqpq5Shimmer)
    input_values.append(apq11Shimmer)
    input_values.append(hnr05)
    input_values.append(hnr15)
    input_values.append(hnr25)
    input_values.append(hnr35)
    input_values.append(hnr38)

    os.remove(cwd+"/"+voiceData.filename) 
    
    final = np.array(input_values)
    data_unseen = pd.DataFrame([final],columns = cols)
    prediction  = predict_model(model , data = data_unseen )
    print(prediction.Label[0])
    if prediction.Label[0] == 1:
        return "The Model detects that this person has Parkinson's Disease. Please get proper Medical Attention."
    else:
        return "The Model detects that this person doesn't have Parkinson's Disease. Have Fun!"
        

if __name__ == '__main__':
    app.run()
