# PERFORMANCE PATTERNS

## 3D Optimization: High-Density Instances (Source: Pattern #7)

**Goal**: Render thousands of identical/similar objects (e.g., Rubik's stickers, points) at 60fps.

### Strategy: InstancedMesh
- Use `THREE.InstancedMesh` instead of standard `THREE.Mesh` or `THREE.Group`.
- **Draw Calls**: Reduces calls from $O(N)$ to $O(1)$.

### Matrix Manipulation
Because instanced objects cannot be grouped in the scene graph for rotations, you must manipulate their matrices directly:
1. **Identify**: Use a logical grid/index to find the instance IDs for a specific transformation (e.g., a Rubik's "slice").
2. **Transform**: 
   ```javascript
   // Apply rotation to current matrix
   tempMatrix.makeRotationAxis(axis, angle);
   instanceMatrix.multiplyMatrices(tempMatrix, instanceMatrix);
   mesh.setMatrixAt(id, instanceMatrix);
   ```
3. **Commit**: Set `mesh.instanceMatrix.needsUpdate = True`.
