const express = require('express');
const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
require('dotenv').config(); // To load .env for WHATSAPP_TARGET_NUMBER if needed here

const app = express();
const port = process.env.NODE_PORT || 8080;

app.use(express.json());

const client = new Client({
    authStrategy: new LocalAuth({dataPath: "wwebjs_auth"}), // Persist session
    puppeteer: {
        headless: true, // Run in background
        // args: ['--no-sandbox', '--disable-setuid-sandbox'] // Uncomment if running in some Linux environments
    }
});

client.on('qr', qr => {
    qrcode.generate(qr, { small: true });
    console.log('QR RECEIVED', qr);
    console.log('Scan the QR code with your WhatsApp linked devices option.');
});

client.on('authenticated', () => {
    console.log('WhatsApp Authenticated!');
});

client.on('auth_failure', msg => {
    console.error('WhatsApp Authentication failure:', msg);
    // Consider exiting or attempting to re-initialize
});

client.on('ready', () => {
    console.log('WhatsApp Client is ready!');
});

client.on('disconnected', (reason) => {
    console.log('Client was logged out', reason);
    // Consider re-initializing or exiting
});

client.initialize().catch(err => console.error("Error during WhatsApp client initialization:", err));

app.post('/send-message', async (req, res) => {
    const { targetNumber, messageText } = req.body;

    if (!targetNumber || !messageText) {
        return res.status(400).json({ success: false, error: 'targetNumber and messageText are required.' });
    }

    if (client.info && client.info.wid) { // Check if client is ready
        try {
            const chatId = `${targetNumber}@c.us`; // Format number for whatsapp-web.js
            await client.sendMessage(chatId, messageText);
            console.log(`Message sent to ${targetNumber}: ${messageText}`);
            res.json({ success: true, message: 'Message sent successfully.' });
        } catch (error) {
            console.error('Error sending WhatsApp message:', error);
            res.status(500).json({ success: false, error: 'Failed to send message.', details: error.message });
        }
    } else {
        console.warn('WhatsApp client not ready, message not sent.');
        res.status(503).json({ success: false, error: 'WhatsApp client not ready. Please scan QR code or wait for initialization.' });
    }
});

app.listen(port, () => {
    console.log(`WhatsApp service listening on port ${port}`);
});