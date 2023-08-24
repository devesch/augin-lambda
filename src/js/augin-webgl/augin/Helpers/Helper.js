export class Helper
{
    static getUint64(dataView, byteOffset) {
        const lowerUint32 = dataView.getUint32(byteOffset);
        const upperUint32 = dataView.getUint32(byteOffset + 4);
        return (upperUint32 << 32) + lowerUint32;
    }

    static readString32(dataView, index) {
        const sizeOfText = dataView.getUint32(index, true);
        index += 4;
        const text = Helper.convertToString(dataView, index, sizeOfText);
        index += sizeOfText;
        return [index, text];
    }

    static convertToString(dataView, startIndex, length) {
        const uint8Array = new Uint8Array(dataView.buffer, startIndex, length);
        const decoder = new TextDecoder('utf-8');
        return decoder.decode(uint8Array);
    }

}