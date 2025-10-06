// Hello World in JavaScript
console.log("Hello, World!");

const readline = require('readline');
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

rl.question("Enter your name: ", (name) => {
    console.log(`Hello, ${name}! Welcome to UMLC!`);
    rl.close();
});
