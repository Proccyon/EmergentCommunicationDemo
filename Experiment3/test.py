import pyglet

# Create a window
window = pyglet.window.Window(800, 600)

# Create a batch for static objects
static_batch = pyglet.graphics.Batch()

# Define static objects - they don't change, so add them to the batch
# For example, creating static rectangles
static_rectangle_1 = pyglet.shapes.Rectangle(50, 100, 200, 150, color=(50, 225, 30), batch=static_batch)
static_rectangle_2 = pyglet.shapes.Rectangle(300, 200, 150, 100, color=(225, 50, 50), batch=static_batch)

# Dynamic object - this will change position every frame
dynamic_circle = pyglet.shapes.Circle(400, 300, 50, color=(50, 50, 225), batch=static_batch)

x = 400

# Update function
def update(dt):
    # Move the dynamic object, for example, move right by 5 pixels per frame
    dynamic_circle.x += 5
    if dynamic_circle.x > window.width:
        rec3 = pyglet.shapes.Rectangle(340, 200, 150, 100, color=(225, 50, 50), batch=static_batch)
        dynamic_circle.x = 0

# Draw everything
@window.event
def on_draw():
    window.clear()
    static_batch.draw()  # Draw all static objects
    dynamic_circle.draw()  # Draw the dynamic object

# Schedule the update function
pyglet.clock.schedule_interval(update, 1/60.0)  # 60 updates per second

# Run the Pyglet app
pyglet.app.run()