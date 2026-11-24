// 客户端图片压缩：上传前把图片压到指定字节数以内，降低带宽与失败率。
// 仅处理浏览器 Canvas 可解码的格式（jpeg/png/webp），HEIC/GIF/BMP 等原样返回。

const DEFAULT_MAX_BYTES = 1024 * 1024 // 1MB
const DEFAULT_MAX_DIMENSION = 1920 // 最长边像素
const DEFAULT_QUALITY = 0.8
const MIN_QUALITY = 0.3

const COMPRESSIBLE = ['image/jpeg', 'image/png', 'image/webp']

/**
 * 压缩图片。返回 Promise<File|Blob>：
 * - 小于目标字节数、或浏览器无法解码的格式 → 返回原文件
 * - 需要压缩时 → 缩放 + 迭代降低 JPEG 质量，直到 <= maxBytes
 */
export function compressImage(
  file,
  { maxBytes = DEFAULT_MAX_BYTES, maxDimension = DEFAULT_MAX_DIMENSION } = {}
) {
  return new Promise((resolve, reject) => {
    if (!file || !file.type || !file.type.startsWith('image/')) {
      resolve(file)
      return
    }
    if (!COMPRESSIBLE.includes(file.type)) {
      resolve(file) // HEIC/GIF/BMP 等：canvas 无法可靠解码，原样上传
      return
    }
    if (file.size <= maxBytes) {
      resolve(file)
      return
    }

    const url = URL.createObjectURL(file)
    const img = new Image()

    img.onload = () => {
      URL.revokeObjectURL(url)
      try {
        let { width, height } = img
        const maxDim = Math.max(width, height)
        if (maxDim > maxDimension) {
          const ratio = maxDimension / maxDim
          width = Math.round(width * ratio)
          height = Math.round(height * ratio)
        }

        const canvas = document.createElement('canvas')
        canvas.width = width
        canvas.height = height
        const ctx = canvas.getContext('2d')
        ctx.drawImage(img, 0, 0, width, height)

        const step = (quality) => {
          canvas.toBlob(
            (blob) => {
              if (!blob) {
                resolve(file) // 压缩失败兜底，用原图
                return
              }
              if (blob.size <= maxBytes || quality <= MIN_QUALITY) {
                resolve(blob)
              } else {
                step(quality - 0.1)
              }
            },
            'image/jpeg',
            quality
          )
        }
        step(DEFAULT_QUALITY)
      } catch (e) {
        resolve(file)
      }
    }

    img.onerror = () => {
      URL.revokeObjectURL(url)
      resolve(file) // 解码失败（如部分 HEIC），用原图
    }
    img.src = url
  })
}
