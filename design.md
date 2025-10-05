# Alchemy Game Design (Pygame)

## Overview
A large window divided into four main interactive areas:
- **Mine (Top Left)**
- **Inventory (Top Right)**
- **Crafting (Bottom Left)**
- **Garden (Bottom Right)**

---

## Areas

### 1. Mine (Top Left)
- Gray window with a grid of tiles:
  - Rock: gray square
  - Quartzium: gray square with white horizontal stripes
  - Other minerals: unique textures/colors
- **Fog of war** mechanic: unexplored tiles are hidden.
- **Regenerate** button in the top left resets the mine.

### 2. Inventory (Top Right)
- Displays all materials the player owns (with textures).
- Shows a number below each item indicating quantity.
- Items with a count of 0 are hidden.

### 3. Crafting (Bottom Left)
- Contains two slots for combining items.
- Drag and drop minerals from inventory into slots:
  - Number decrements immediately when dragging starts.
  - If dropped outside a slot, the item returns to inventory.
  - If dropped into a filled slot, items swap and the previous item returns to inventory.
- **Combine** button (yellow):
  - If a valid recipe exists, produces the result and empties slots.
  - If not, spawns 15 "BOOM!" texts (random red/yellow/orange colors) that fly and disappear, and both items are lost.

### 4. Garden (Bottom Right)
- Plants grow here.
- Clicking a plant removes it and adds resources to inventory.

---

## Notes
- All UI elements should be visually distinct and clearly separated.
- Drag-and-drop and feedback mechanics should be intuitive and responsive.




## original
lets make a alchemy game in pygame

theres gonna be a huyge windwo with 4 parts:


- top left: mine. it wil lbe a gray window with a grid of either gray square (rock), gray square with white horixontal stripes (quartzium), or some other minerals. add a fog of war mechanic to the mine. It regenerates when you press the regen button in the top left.
- top right: inventory. it has all materials textures and a number below them saying how many you have. ones with 0 are not displayed.
- bottom left: crafting. it has a grid where you can combine items to make more. there are two slots and you can drag 1 mineral from the inventory into either slot. make sure thast if you dont finish dragging into a slot the item doesnt dissapear number go back up, and the number decrements immidiatly when you start dragging, and if you drag into a filled slot it swaps with the thing in it and retursn that to inve. it has a yellow combine butotin that tries to combine them. if it exists, it gives you that and slots become empty. If it doesnt exist, it spawns 15 texts of random colors from red to yellow and orange that sya "BOOM!" that fly everywhere and dissapear, and both items dissapear.
- bottom right: garden. plants grow here. clicking them makes them dissapear and gives you resources. 