const fs = require('fs');
const path = require('path');
const os = require('os');
const Busboy = require('busboy');
const axios = require('axios');
const functions = require('firebase-functions');
const speech = require('@google-cloud/speech');

exports.speechToText = functions.https.onRequest(async (req, res) => {
    const client = new speech.SpeechClient();

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

    const [response] = await client.recognize(request);
    res.json(response.results.length ? response.results[0].alternatives : null);
});
