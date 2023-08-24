export class MathHelper {
    static findPreviousPowerOfTwo(n) {
        let power = Math.floor(Math.log2(n));
        return Math.pow(2, power);
    }
}