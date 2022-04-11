/**
 * Iterates 'fillee' and overwrites its values with any properties present in 'filler'.
 * Changed 'fillee' in-place.
 * @param {object} fillee 
 * @param {object} filler
 * @returns {object} changed fillee object.
 */
export function fillObject(fillee, filler) {
    for (let key in fillee) {
        if (key in filler) {
            fillee[key] = filler[key];
        }
    }
    return state;
}