from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from typing import List, Tuple
import random

app = FastAPI()

app.mount("/", StaticFiles(directory="static", html=True), name="static")

# Dimensões do grid
WIDTH = 20
HEIGHT = 20

# Direções possíveis
DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0)
}

class SnakeGame:
    def __init__(self):
        self.snake = [(WIDTH // 2, HEIGHT // 2)]
        self.food = self.place_food()
        self.direction = random.choice(list(DIRECTIONS.values()))

    def place_food(self):
        while True:
            food = (random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1))
            if food not in self.snake:
                return food

    def move(self):
        head = self.snake[-1]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])

        # Verifica se bateu na parede ou em si mesma
        if (new_head in self.snake or
            new_head[0] < 0 or new_head[0] >= WIDTH or
            new_head[1] < 0 or new_head[1] >= HEIGHT):
            return False

        self.snake.append(new_head)

        # Se comeu a comida
        if new_head == self.food:
            self.food = self.place_food()
        else:
            self.snake.pop(0)

        return True

    def change_direction(self, direction):
        if direction in DIRECTIONS:
            new_direction = DIRECTIONS[direction]
            # Não pode mudar para a direção oposta
            if (new_direction[0] != -self.direction[0] or
                new_direction[1] != -self.direction[1]):
                self.direction = new_direction

game = SnakeGame()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        await websocket.send_json({
            "snake": game.snake,
            "food": game.food
        })

        try:
            data = await websocket.receive_text()
            game.change_direction(data.upper())
        except:
            break

        if not game.move():
            break

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
