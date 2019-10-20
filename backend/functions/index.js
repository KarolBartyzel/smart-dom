const fs = require('fs');
const util = require('util');
const functions = require('firebase-functions');
const speechToText = require('@google-cloud/speech');
const textToSpeech = require('@google-cloud/text-to-speech');
const uuidv4 = require('uuid/v4');

const writeFile = util.promisify(fs.writeFile);

exports.textToSpeech = functions.https.onRequest(async (req, res) => {
    const textToSpeechClient = new textToSpeech.TextToSpeechClient();
    const { text } = req.query;
    console.log('lkala');
    console.log(text);

    const [response] = await textToSpeechClient.synthesizeSpeech({
        input: { text },
        voice: { languageCode: 'pl', ssmlGender: 'NEUTRAL' },
        audioConfig: { audioEncoding: 'MP3' },
    });

    const fileName = `/tmp/${uuidv4()}.mp3`;
    console.log(fileName);
    await writeFile(fileName, response.audioContent, 'binary');
    res.status(200).sendFile(fileName);
})

exports.speechToText = functions.https.onRequest(async (req, res) => {
    const speechToTextClient = new speechToText.SpeechClient();

    const request = {
        audio: {
            content: Buffer.from(req.body).toString('base64'),
        },
        config: {
            encoding: 'LINEAR16',
            sampleRateHertz: 41000,
            languageCode: 'pl',
        },
    };

    const [response] = await speechToTextClient.recognize(request);
    res.json(response.results.length ? response.results[0].alternatives : null);
});
