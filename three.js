class PingPongGame {
    constructor() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer();

        this.colors = {
            green: 0x00ff00,
            magenta: 0xff00ff,
            black: 0x000000,
            white: 0xffffff
        };

        this.gameMode = null;
        this.players = [];
        this.ball = null;
        this.table = null;
        this.scores = [];
        this.maxScore = 5;

        this.init();
    }

    init() {
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(this.renderer.domElement);

        this.camera.position.z = 15;
        this.camera.position.y = 5;

        // Initialize OrbitControls here
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);

        this.createTable();
        this.createBall();
        this.createLights();

        this.animate();
    }

    createTable() {
        const geometry = new THREE.BoxGeometry(10, 0.2, 6);
        const material = new THREE.MeshPhongMaterial({ color: this.colors.green });
        this.table = new THREE.Mesh(geometry, material);
        this.scene.add(this.table);
    }

    createBall() {
        const geometry = new THREE.SphereGeometry(0.1, 32, 32);
        const material = new THREE.MeshPhongMaterial({ color: this.colors.white });
        this.ball = new THREE.Mesh(geometry, material);
        this.ball.position.y = 1;
        this.scene.add(this.ball);

        // Initialize ball velocity
        this.ball.velocity = new THREE.Vector3(0.05, 0, 0.05);
    }

    createLights() {
        const ambientLight = new THREE.AmbientLight(0x404040);
        this.scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0xffffff, 1, 100);
        pointLight.position.set(0, 10, 0);
        this.scene.add(pointLight);
    }

    createPaddle(color, position) {
        const geometry = new THREE.BoxGeometry(0.2, 0.5, 1);
        const material = new THREE.MeshPhongMaterial({ color: color });
        const paddle = new THREE.Mesh(geometry, material);
        paddle.position.copy(position);
        this.scene.add(paddle);
        return paddle;
    }

    setGameMode(mode) {
        this.gameMode = mode;
        this.players = [];
        this.scores = [];

        switch (mode) {
            case '1v1':
                this.players.push(this.createPaddle(this.colors.magenta, new THREE.Vector3(-5, 1, 0)));
                this.players.push(this.createPaddle(this.colors.black, new THREE.Vector3(5, 1, 0)));
                this.scores = [0, 0];
                break;
            case '1vAI':
                this.players.push(this.createPaddle(this.colors.magenta, new THREE.Vector3(-5, 1, 0)));
                this.players.push(this.createPaddle(this.colors.black, new THREE.Vector3(5, 1, 0)));
                this.scores = [0, 0];
                break;
            case '4players':
                this.players.push(this.createPaddle(this.colors.magenta, new THREE.Vector3(-5, 1, 0)));
                this.players.push(this.createPaddle(this.colors.black, new THREE.Vector3(5, 1, 0)));
                this.players.push(this.createPaddle(this.colors.green, new THREE.Vector3(0, 1, -3)));
                this.players.push(this.createPaddle(this.colors.white, new THREE.Vector3(0, 1, 3)));
                this.scores = [0, 0, 0, 0];
                break;
        }
    }

    updateBall() {
        this.ball.position.add(this.ball.velocity);

        // Check collisions with table edges
        if (Math.abs(this.ball.position.x) > 5 || Math.abs(this.ball.position.z) > 3) {
            this.ball.velocity.multiplyScalar(-1);
        }

        // Check collisions with paddles
        this.players.forEach((paddle, index) => {
            if (this.ball.position.distanceTo(paddle.position) < 0.6) {
                this.ball.velocity.multiplyScalar(-1);
                this.scores[index]++;

                // Increase ball speed, but not too much
                const currentSpeed = this.ball.velocity.length();
                if (currentSpeed < 0.2) {
                    this.ball.velocity.normalize().multiplyScalar(currentSpeed * 1.1);
                }
            }
        });

        // Check for win condition
        const winnerIndex = this.scores.findIndex(score => score >= this.maxScore);
        if (winnerIndex !== -1) {
            this.endGame(winnerIndex);
        }
    }

    updateAI() {
        if (this.gameMode === '1vAI') {
            const aiPaddle = this.players[1];
            aiPaddle.position.z += (this.ball.position.z - aiPaddle.position.z) * 0.1;
            aiPaddle.position.z = THREE.MathUtils.clamp(aiPaddle.position.z, -2.5, 2.5);
        }
    }

    endGame(winnerIndex) {
        const winner = ['Player 1', 'Player 2', 'Player 3', 'Player 4'][winnerIndex];
        alert(`Congratulations ${winner}! You've won the game!`);
        this.showMenu();
    }

    showMenu() {
        const menu = document.createElement('div');
        menu.style.position = 'absolute';
        menu.style.top = '50%';
        menu.style.left = '50%';
        menu.style.transform = 'translate(-50%, -50%)';
        menu.style.background = 'white';
        menu.style.padding = '20px';
        menu.innerHTML = `
            <h2>Choose Game Mode</h2>
            <button onclick="game.setGameMode('1v1')">1v1</button>
            <button onclick="game.setGameMode('1vAI')">1 vs AI</button>
            <button onclick="game.setGameMode('4players')">4 Players</button>
        `;
        document.body.appendChild(menu);
    }

    animate() {
        requestAnimationFrame(() => this.animate());

        if (this.gameMode) {
            this.updateBall();
            this.updateAI();
        }

        this.renderer.render(this.scene, this.camera);
    }
}

const game = new PingPongGame();
game.showMenu();


document.addEventListener('DOMContentLoaded', () => {
    const game = new PingPongGame();
    game.showMenu();

    // Add event listeners for player controls
    document.addEventListener('keydown', (event) => {
        if (game.gameMode) {
            const player1 = game.players[0];
            const player2 = game.players[1];

            switch (event.key) {
                case 'ArrowUp':
                    player2.position.z = Math.max(player2.position.z - 0.5, -2.5);
                    break;
                case 'ArrowDown':
                    player2.position.z = Math.min(player2.position.z + 0.5, 2.5);
                    break;
                case 'w':
                    player1.position.z = Math.max(player1.position.z - 0.5, -2.5);
                    break;
                case 's':
                    player1.position.z = Math.min(player1.position.z + 0.5, 2.5);
                    break;
            }
        }
    });
});