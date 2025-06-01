import imageio

frames = [
    imageio.imread(f"imgs/{i:05d}.jpg") for i in range(0, 70, 4)
]
frames = frames + frames[::-1]
print(len(frames))
imageio.mimsave('./heart.gif', # output gif
                frames,          # array of input frames
                format='GIF', fps=60, loop=0)         # optional: frames per second