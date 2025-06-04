// Basic Tetris implementation with login and leaderboard using localStorage
const canvas = document.getElementById('tetris');
const ctx = canvas.getContext('2d');
const ROWS = 20;
const COLS = 10;
const BLOCK = 30;
canvas.width = COLS * BLOCK;
canvas.height = ROWS * BLOCK;
ctx.scale(BLOCK, BLOCK);

const COLORS = {
    'I': '#0ff',
    'J': '#00f',
    'L': '#f60',
    'O': '#ff0',
    'S': '#0f0',
    'T': '#f0f',
    'Z': '#f00'
};

const SHAPES = {
    'I': [[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]],
    'J': [[1,0,0],[1,1,1],[0,0,0]],
    'L': [[0,0,1],[1,1,1],[0,0,0]],
    'O': [[1,1],[1,1]],
    'S': [[0,1,1],[1,1,0],[0,0,0]],
    'T': [[0,1,0],[1,1,1],[0,0,0]],
    'Z': [[1,1,0],[0,1,1],[0,0,0]]
};

let grid = createMatrix(COLS, ROWS);
let currentPiece = null;
let dropCounter = 0;
let dropInterval = 1000;
let lastTime = 0;
let score = 0;
let currentUser = null;

const loginScreen = document.getElementById('login-screen');
const gameScreen = document.getElementById('game-screen');
const leaderboardScreen = document.getElementById('leaderboard-screen');

function createMatrix(w, h) {
    const matrix = [];
    while (h--) matrix.push(new Array(w).fill(0));
    return matrix;
}

function collide(matrix, piece) {
    for (let y = 0; y < piece.matrix.length; ++y) {
        for (let x = 0; x < piece.matrix[y].length; ++x) {
            if (piece.matrix[y][x] &&
                (matrix[y + piece.pos.y] &&
                 matrix[y + piece.pos.y][x + piece.pos.x]) !== 0) {
                return true;
            }
        }
    }
    return false;
}

function merge(matrix, piece) {
    piece.matrix.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value) matrix[y + piece.pos.y][x + piece.pos.x] = value;
        });
    });
}

function rotate(matrix) {
    const N = matrix.length;
    const result = matrix.map((_, i) => matrix.map(row => row[i]).reverse());
    return result;
}

function playerReset() {
    const types = 'IJLOSTZ';
    const type = types[Math.floor(Math.random() * types.length)];
    currentPiece = {
        pos: {x: (COLS/2|0) - 1, y: 0},
        matrix: SHAPES[type],
        color: COLORS[type]
    };
    if (collide(grid, currentPiece)) {
        grid.forEach(row => row.fill(0));
        updateScore();
        score = 0;
    }
}

function sweep() {
    outer: for (let y = grid.length - 1; y >= 0; --y) {
        for (let x = 0; x < grid[y].length; ++x) {
            if (grid[y][x] === 0) continue outer;
        }
        const row = grid.splice(y, 1)[0].fill(0);
        grid.unshift(row);
        ++y;
        score += 10;
    }
}

function drawMatrix(matrix, offset) {
    matrix.forEach((row, y) => {
        row.forEach((value, x) => {
            if (value) {
                ctx.fillStyle = currentPiece.color;
                ctx.fillRect(x + offset.x, y + offset.y, 1, 1);
                ctx.strokeStyle = '#333';
                ctx.strokeRect(x + offset.x, y + offset.y, 1, 1);
            }
        });
    });
}

function draw() {
    ctx.fillStyle = '#88e';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    drawMatrix(grid, {x:0, y:0});
    drawMatrix(currentPiece.matrix, currentPiece.pos);
}

function update(time = 0) {
    const delta = time - lastTime;
    lastTime = time;
    dropCounter += delta;
    if (dropCounter > dropInterval) {
        playerDrop();
    }
    draw();
    requestAnimationFrame(update);
}

function playerDrop() {
    currentPiece.pos.y++;
    if (collide(grid, currentPiece)) {
        currentPiece.pos.y--;
        merge(grid, currentPiece);
        sweep();
        playerReset();
    }
    dropCounter = 0;
    updateScore();
}

function playerMove(dir) {
    currentPiece.pos.x += dir;
    if (collide(grid, currentPiece)) currentPiece.pos.x -= dir;
}

function playerRotate() {
    const rotated = rotate(currentPiece.matrix);
    const oldX = currentPiece.pos.x;
    currentPiece.pos.x += 1;
    if (collide(grid, {matrix: rotated, pos: currentPiece.pos})) {
        currentPiece.pos.x = oldX;
        return;
    }
    currentPiece.matrix = rotated;
}

function updateScore() {
    document.getElementById('score').textContent = 'Score: ' + score;
}

function saveScore() {
    const users = JSON.parse(localStorage.getItem('users') || '{}');
    users[currentUser].score = Math.max(users[currentUser].score || 0, score);
    localStorage.setItem('users', JSON.stringify(users));
}

function showLeaderboard() {
    const list = document.getElementById('leaderboard-list');
    list.innerHTML = '';
    const users = JSON.parse(localStorage.getItem('users') || '{}');
    const entries = Object.entries(users).sort((a,b) => (b[1].score||0)-(a[1].score||0));
    entries.slice(0,10).forEach(([user,data]) => {
        const li = document.createElement('li');
        li.textContent = `${user}: ${data.score||0}`;
        list.appendChild(li);
    });
}

// Login handling
const loginForm = document.getElementById('login-form');
loginForm.addEventListener('submit', evt => {
    evt.preventDefault();
    const name = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    const users = JSON.parse(localStorage.getItem('users') || '{}');
    if (!users[name]) {
        users[name] = {password: pass, score:0};
    } else if (users[name].password !== pass) {
        alert('Invalid password');
        return;
    }
    localStorage.setItem('users', JSON.stringify(users));
    currentUser = name;
    document.getElementById('current-user').textContent = 'Player: '+name;
    loginScreen.classList.add('hidden');
    gameScreen.classList.remove('hidden');
    playerReset();
    updateScore();
    update();
});

document.getElementById('logout').addEventListener('click', () => {
    saveScore();
    currentUser = null;
    gameScreen.classList.add('hidden');
    leaderboardScreen.classList.add('hidden');
    loginScreen.classList.remove('hidden');
});

document.getElementById('show-leaderboard').addEventListener('click', () => {
    saveScore();
    showLeaderboard();
    gameScreen.classList.add('hidden');
    leaderboardScreen.classList.remove('hidden');
});

document.getElementById('back-to-game').addEventListener('click', () => {
    leaderboardScreen.classList.add('hidden');
    gameScreen.classList.remove('hidden');
});

// Input handling
document.addEventListener('keydown', e => {
    if (!currentPiece) return;
    if (e.code === 'ArrowLeft') playerMove(-1);
    else if (e.code === 'ArrowRight') playerMove(1);
    else if (e.code === 'ArrowDown') playerDrop();
    else if (e.code === 'ArrowUp') playerRotate();
    else if (e.code === 'Space') {
        while(!collide(grid, currentPiece)) currentPiece.pos.y++;
        currentPiece.pos.y--;
        merge(grid, currentPiece);
        sweep();
        playerReset();
        updateScore();
    }
});
