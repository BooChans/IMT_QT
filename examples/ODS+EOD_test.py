from ifmta.ifta import Ifta, IftaImproved
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from automatic_sizing import zero_pad

img_path = "assets/fabichou.jpg"

img = Image.open(img_path).convert("L")
img.thumbnail((256,256),Image.LANCZOS)
img = np.array(img)
img = img/img.max()
img = zero_pad(np.array([img]), (512,512)).squeeze()

plt.imshow(img)
plt.show()

eod = IftaImproved(img, n_levels=4)


plt.imshow(eod[-1])
plt.show()
np.save("assets/eod_enh.npy", eod[-1])


