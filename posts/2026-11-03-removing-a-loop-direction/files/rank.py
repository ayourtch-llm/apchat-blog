import torch
m = torch.load("acts-250.pt")["mean"]
rd = m["res_loop"] - m["res_pre"]; md = m["mlp_loop"] - m["mlp_pre"]
L = rd.shape[0]
print("layer |resdiff| |res_pre| rel |mlpdiff| mlpdiff.d22 cos(res_i,res_22)")
d = rd[22] / rd[22].norm()
for i in range(L):
    rp = m["res_pre"][i].norm()
    print(f"{i:2d} {rd[i].norm():8.2f} {rp:8.2f} {rd[i].norm()/rp:5.2f} {md[i].norm():7.2f} {(md[i]@d):7.2f} {torch.nn.functional.cosine_similarity(rd[i], rd[22], dim=0):5.2f}")
