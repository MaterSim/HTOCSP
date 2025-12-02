from rdkit import Chem
from rdkit.Chem import AllChem, Draw, rdDepictor
import matplotlib.pyplot as plt
from cairosvg import svg2png
from io import BytesIO
from PIL import Image
import math

# Define the molecules
T1 = [
#("TTBI", "\t$P\overline{1}$, Z$^\prime$=1\n\t\t$P4_2$/$m$, Z$^\prime$=**\n\t\t\t$P6_3/mmm$, Z$^\prime$=0.1", "C1=C2C3C4=CC5=C(C=C4C(C2=CC6=C1NC(=O)N6)C7=CC8=C(C=C37)NC(=O)N8)NC(=O)N5"),
("ZJU-HOF-60", "$C$2/$m$", "O=C(O)c2cc(C#Cc1cc(C(=O)O)cc(C(=O)O)c1)cc(C(=O)O)c2"),
("ZJU-HOF-62", "$P3_1$", "O=C(O)c2cc(C#CC#Cc1cc(C(=O)O)cc(C(=O)O)c1)cc(C(=O)O)c2"),
("TTBI", "$P\overline{1}$; $P4_2$/$m$; $P6_3/mmm$", "O=c2[nH]c1cc5c(cc1[nH]2)C8c4cc3[nH]c(=O)[nH]c3cc4C5c7cc6[nH]c(=O)[nH]c6cc78"),
("TCF", "$I\overline{4}$", "O=C(O)c4ccc(C(c1ccc(C(=O)O)cc1)(c2ccc(C(=O)O)cc2)c3ccc(C(=O)O)cc3)cc4"),
#("HOF-1a", "$Fdd2$ (0.5)", "Nc8nc(N)nc(c7ccc(C(c2ccc(c1nc(N)nc(N)n1)cc2)(c4ccc(c3nc(N)nc(N)n3)cc4)c6ccc(c5nc(N)nc(N)n5)cc6)cc7)n8"),
("HOF-5a", "$C$2/$m$", "Nc8nc(N)nc(c7ccc(/C(=C(c2ccc(c1nc(N)nc(N)n1)cc2)/c4ccc(c3nc(N)nc(N)n3)cc4)c6ccc(c5nc(N)nc(N)n5)cc6)cc7)n8"),
]
# Create the plot with GridSpec
fig = plt.figure(figsize=(15, 6))
gs = fig.add_gridspec(
    2,
    3,
    width_ratios=[1.4, 1.4, 1.7],
    height_ratios=[1, 1.25],
    wspace=0,
    hspace=0,
)
rdDepictor.SetPreferCoordGen(True)
# Place the first 10 molecules in the first row
for i in range(4):
    row = i // 2
    col = i % 2
    ax = fig.add_subplot(gs[row, col])
    # Extract molecule data
    name, spg, smiles = T1[i]

    # Generate RDKit molecule object from SMILES string
    mol = Chem.MolFromSmiles(smiles)
    AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
    AllChem.UFFOptimizeMolecule(mol)
    AllChem.Compute2DCoords(mol)
    if name == "TTBI":
        ang = 10
    elif name == "ZJU-HOF-60" or name == "ZJU-HOF-62":
        ang = 30
    else:
        ang = 0
    conf = mol.GetConformer()
    for i in range(mol.GetNumAtoms()):
        pos = conf.GetAtomPosition(i)
        angle = math.radians(ang)  # Rotate by 30 degrees
        x_new = pos.x * math.cos(angle) - pos.y * math.sin(angle)
        y_new = pos.x * math.sin(angle) + pos.y * math.cos(angle)
        conf.SetAtomPosition(i, (x_new, y_new, pos.z))

    if name == "ZJU-HOF-62":
        drawer = Draw.MolDraw2DSVG(500, 350)
    else:
        drawer = Draw.MolDraw2DSVG(400, 280)
    # Remove background and padding to avoid internal borders in the SVG/PNG
    drawer.drawOptions().clearBackground = False
    drawer.drawOptions().padding = 0.0
    drawer.DrawMolecule(mol)
    drawer.FinishDrawing()
    svg = drawer.GetDrawingText()
    if name == "ZJU-HOF-62":
        png_image = svg2png(bytestring=svg, output_width=1200, output_height=800)
    else:
        png_image = svg2png(bytestring=svg, output_width=950, output_height=800)
    png_image = Image.open(BytesIO(png_image))

    # Display the PNG on the subplot
    ax.imshow(png_image)
    ax.axis('off')
    # Ensure no visible frame/spines around each subplot
    ax.set_frame_on(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.patch.set_visible(False)
    ax.set_title(f"{name}", fontsize=15, va='center')

# Add a larger subplot for the last molecule
ax = fig.add_subplot(gs[:, 2])
name, spg, smiles = T1[4]
mol = Chem.MolFromSmiles(smiles)
AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
AllChem.UFFOptimizeMolecule(mol)
AllChem.Compute2DCoords(mol)
drawer = Draw.MolDraw2DSVG(500, 600)
# Remove background and padding to avoid internal borders in the SVG/PNG
drawer.drawOptions().clearBackground = False
drawer.drawOptions().padding = 0.0
drawer.DrawMolecule(mol)
drawer.FinishDrawing()
svg = drawer.GetDrawingText()
png_image = svg2png(bytestring=svg, output_width=1500, output_height=1800)
png_image = Image.open(BytesIO(png_image))
# Display the PNG on the subplot
ax.imshow(png_image)
ax.axis('off')
# Ensure no visible frame/spines around the large subplot
ax.set_frame_on(False)
for spine in ax.spines.values():
    spine.set_visible(False)
ax.patch.set_visible(False)
ax.set_title(f"{name}", fontsize=15, va='center')

# Adjust layout to prevent overlap
# Fill the canvas fully with no margins between/around axes
plt.subplots_adjust(left=0, right=1, bottom=0, top=1, wspace=0, hspace=0)
plt.savefig('Fig1-molecule.pdf', bbox_inches='tight', pad_inches=0.5)
