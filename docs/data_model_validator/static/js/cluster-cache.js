// Shared cache for cluster + validation data used by the results view and modal.
// Avoids leaking large objects onto `window` and keeps the coupling explicit.

const cache = new Map();

function key(endpointId, clusterId) {
  return `${endpointId}_${clusterId}`;
}

export function setClusterCache(endpointId, clusterId, payload) {
  cache.set(key(endpointId, clusterId), payload);
}

export function getClusterCache(endpointId, clusterId) {
  return cache.get(key(endpointId, clusterId)) || null;
}

export function clearClusterCache() {
  cache.clear();
}


