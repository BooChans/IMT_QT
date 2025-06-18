from ifmta.ifta import Ifta
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from diffraction_propagation import far_field
from automatic_sizing import zero_pad

img_path = "assets/christofou.jpg"

img = Image.open(img_path)
img = img.convert("L")
img = np.array(img)


EOD = Ifta(img, n_levels=4)

print(type(EOD))

plt.figure()
plt.imshow(EOD)

max_ = max(EOD.shape)

U0 = np.exp(-1j*EOD)
U0 = np.repeat(U0[np.newaxis, :, :], 1, axis=0)
U0 = zero_pad(U0, (max_,max_))
Uz = far_field(U0, wavelength=0.633, z = 1e6, dx = 1.0).transpose(0,2,1)

plt.figure()
plt.imshow(np.squeeze(Uz))


plt.show()



