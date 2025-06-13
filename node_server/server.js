//@ts-check

// Filename - server.js

const mysql = require('mysql2');
const express = require('express');
const app = express();
const fs = require('fs');
const bodyParser = require('body-parser');
const cors = require('cors');
const { exec } = require("child_process");
const { v4: uuidv4 } = require('uuid'); // npm install uuid
const WebSocket = require('ws');        // npm install ws
const port = 3000;
const WS_PORT = 5000;

const GEPHI_PATH = "/app/graph_files";

// Optional MySQL setup (commented out)

const connection = mysql.createConnection({
    host: 'host.docker.internal',
    port: 3306,
    database: 'collaboration_network',
    user: 'root',
    password: process.env.DATABASE_PASSWORD
});


// Express middleware setup
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(cors());

// Store pending responses using request ID
const pendingResponses = {};

// WebSocket server setup (Python should connect to this)
const wss = new WebSocket.Server({ port: WS_PORT }, () => {
    console.log(`WebSocket server listening on port ${WS_PORT}`);
});

wss.on('connection', (ws) => {
    console.log('Python connected via WebSocket');

    ws.on('message', (message) => {
        try {
            //@ts-ignore
            const data = JSON.parse(message);
            const id = data.id;
            const content = data.content
            if (pendingResponses[id]) {
                switch (data.type) {
                    case "topic":
                        const { graph, category, authors, papers } = content;
                        console.log("The category is: " + category)
                        pendingResponses[id].callback({ graph, authors, papers });
                        break;
                    case "author":
                        const searchAuthors = content;
                        console.log(content);
                        pendingResponses[id].callback({ searchAuthors });
                        break;
                    default:
                        console.log("Unknown request")
                        break
                }
                clearTimeout(pendingResponses[id].timeout);
                delete pendingResponses[id];
            } else {
                console.warn(`No pending request found for ID: ${id}`);
            }

        } catch (err) {
            console.error("Failed to parse message from Python:", err);
        }
    });

    ws.on('close', () => {
        console.log('Python WebSocket disconnected');
    });

    ws.on('error', (err) => {
        console.error('WebSocket error:', err);
    });
});

// POST endpoint to trigger Python script and expect WebSocket response
app.post('/send', (req, res) => {
    const requestId = uuidv4();
    const keyword = req.body.keyword;
    console.log("Received keyword:", keyword);
    console.log("Generated request ID:", requestId);

    let command = "python3 /app/'Back End'/main.py ";
    command += (keyword !== "None") ? `1 ${keyword} ` : "2 ";
    command += requestId;

    console.log("Executing command:", command);

    // Set timeout for fallback
    const timeout = setTimeout(() => {
        if (pendingResponses[requestId]) {
            delete pendingResponses[requestId];
            res.status(504).send("Timeout waiting for Python response.");
        }
    }, 100000);

    // Save callback for WebSocket to resolve later
    pendingResponses[requestId] = {
        callback: ({ graph, authors, papers }) => {
            res.setHeader('Content-Type', 'application/json');
            res.status(200).send({ graph, authors, papers });
        },
        timeout
    };

    // Execute Python script
    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Exec error: ${error.message}`);
            clearTimeout(timeout);
            delete pendingResponses[requestId];
            return res.status(500).send('Failed to execute Python script.');
        }
        if (stderr) {
            console.error(`Exec stderr: ${stderr}`);
        }
    });
});

app.post('/search', (req, res) => {
    const requestId = uuidv4();
    const keyword = req.body.keyword;
    const command = "python3 /app/'Back End'/search_author.py " +
        keyword +
        " " +
        requestId
    console.log("Received author:", keyword);
    console.log("Generated request ID:", requestId);
    const timeout = setTimeout(() => {
        if (pendingResponses[requestId]) {
            delete pendingResponses[requestId];
            res.status(504).send("Timeout waiting for Python response.");
        }
    }, 100000);

    pendingResponses[requestId] = {
        callback: ({ searchAuthors }) => {
            console.log('author searched')
            res.status(200).send(searchAuthors.authors);
        },
        timeout
    }
    exec(command, (error, stdout, stderr) => {
        if (error) {
            console.error(`Exec error: ${error.message}`);
            clearTimeout(timeout);
            delete pendingResponses[requestId];
            return res.status(500).send('Failed to execute Python script.');
        }
        if (stderr) {
            console.error(`Exec stderr: ${stderr}`);
        }
    });
})

app.post('/papers', (req, res) => {
    const authorId = req.body.authorID;
    connection.query(
        `
        SELECT DISTINCT title 
        FROM EDGES 
        WHERE author_1 = ` + authorId + ` OR author_2 =` + authorId

        ,
        function (err, result, fields) {
            if (err)
                console.log(err);
            else
                res.send(result);
        }
    )

})

// Start HTTP server
app.listen(port, '0.0.0.0', () => {
    console.log(`HTTP server is running on port ${port}`);
});
