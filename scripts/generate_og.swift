import AppKit
import CoreGraphics
import Foundation

let root = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent()
let outURL = root.appendingPathComponent("assets/og.png")
let iconURL = root.appendingPathComponent("assets/app-icon.png")
let phoneURL = root.appendingPathComponent("assets/screenshots/ko/ss-01.webp")
let photo1URL = root.appendingPathComponent("assets/personas/kr/01-hero-park.webp")
let photo2URL = root.appendingPathComponent("assets/personas/kr/03-snack-smile.webp")

let width = 1200
let height = 630

guard let rep = NSBitmapImageRep(
    bitmapDataPlanes: nil,
    pixelsWide: width,
    pixelsHigh: height,
    bitsPerSample: 8,
    samplesPerPixel: 4,
    hasAlpha: true,
    isPlanar: false,
    colorSpaceName: .deviceRGB,
    bytesPerRow: 0,
    bitsPerPixel: 0
) else {
    fatalError("Failed to create bitmap")
}

NSGraphicsContext.saveGraphicsState()
guard let ctx = NSGraphicsContext(bitmapImageRep: rep) else {
    fatalError("Failed to create graphics context")
}
NSGraphicsContext.current = ctx
let cg = ctx.cgContext

// Warm archival cotton rag paper (#F6F1E9)
NSColor(calibratedRed: 0.965, green: 0.945, blue: 0.914, alpha: 1.0).setFill()
cg.fill(CGRect(x: 0, y: 0, width: width, height: height))

// Subtle oatmeal mat sheet on right
cg.saveGState()
cg.translateBy(x: 938, y: 315)
cg.rotate(by: 2.0 * .pi / 180.0)
let matRect = CGRect(x: -175, y: -235, width: 350, height: 470)
NSColor(calibratedRed: 0.925, green: 0.898, blue: 0.855, alpha: 1.0).setFill()
cg.fill(matRect)
NSColor(calibratedRed: 0.12, green: 0.10, blue: 0.09, alpha: 0.12).setStroke()
cg.stroke(matRect, width: 1)
cg.restoreGState()

func drawMattePrint(_ url: URL, center: CGPoint, size: CGFloat, angleDeg: CGFloat) {
    guard let img = NSImage(contentsOf: url) else { return }
    cg.saveGState()
    cg.translateBy(x: center.x, y: center.y)
    cg.rotate(by: angleDeg * .pi / 180.0)

    let cardRect = CGRect(x: -size / 2 - 9, y: -size / 2 - 20, width: size + 18, height: size + 29)
    cg.saveGState()
    cg.setShadow(offset: CGSize(width: 0, height: -12), blur: 26, color: NSColor(calibratedRed: 0.14, green: 0.10, blue: 0.07, alpha: 0.22).cgColor)
    let cardPath = NSBezierPath(roundedRect: cardRect, xRadius: 3, yRadius: 3)
    NSColor(calibratedRed: 0.988, green: 0.984, blue: 0.973, alpha: 1.0).setFill()
    cardPath.fill()
    cg.restoreGState()

    let imgRect = CGRect(x: -size / 2, y: -size / 2, width: size, height: size)
    img.draw(in: imgRect, from: .zero, operation: .sourceOver, fraction: 1.0)

    NSColor(calibratedRed: 0.12, green: 0.10, blue: 0.09, alpha: 0.12).setStroke()
    cardPath.lineWidth = 1
    cardPath.stroke()
    cg.restoreGState()
}

drawMattePrint(photo1URL, center: CGPoint(x: 785, y: 196), size: 146, angleDeg: 4.5)
drawMattePrint(photo2URL, center: CGPoint(x: 1080, y: 422), size: 132, angleDeg: -5.0)

// Stone-ivory phone frame
let phoneW: CGFloat = 240
let phoneH: CGFloat = 522
let phoneRect = CGRect(x: 932 - phoneW / 2, y: (CGFloat(height) - phoneH) / 2, width: phoneW, height: phoneH)
cg.saveGState()
cg.setShadow(offset: CGSize(width: 0, height: -20), blur: 44, color: NSColor(calibratedRed: 0.14, green: 0.10, blue: 0.07, alpha: 0.28).cgColor)
let bezelRect = phoneRect.insetBy(dx: -7, dy: -7)
let bezelPath = NSBezierPath(roundedRect: bezelRect, xRadius: 36, yRadius: 36)
NSColor(calibratedRed: 0.918, green: 0.890, blue: 0.851, alpha: 1.0).setFill()
bezelPath.fill()
cg.restoreGState()

if let phoneImg = NSImage(contentsOf: phoneURL) {
    cg.saveGState()
    let clip = NSBezierPath(roundedRect: phoneRect, xRadius: 29, yRadius: 29)
    clip.addClip()
    phoneImg.draw(in: phoneRect, from: .zero, operation: .sourceOver, fraction: 1.0)
    cg.restoreGState()
    NSColor(calibratedRed: 0.12, green: 0.10, blue: 0.09, alpha: 0.16).setStroke()
    bezelPath.lineWidth = 1
    bezelPath.stroke()
}

// Top-left masthead mark
if let iconImg = NSImage(contentsOf: iconURL) {
    let iconRect = CGRect(x: 86, y: 504, width: 38, height: 38)
    cg.saveGState()
    let clip = NSBezierPath(roundedRect: iconRect, xRadius: 8, yRadius: 8)
    clip.addClip()
    iconImg.draw(in: iconRect, from: .zero, operation: .sourceOver, fraction: 1.0)
    cg.restoreGState()
}

func serifFont(_ size: CGFloat) -> NSFont {
    return NSFont(name: "AppleMyungjo", size: size) ?? NSFont.systemFont(ofSize: size, weight: .regular)
}
func sansFont(_ size: CGFloat, weight: NSFont.Weight = .regular) -> NSFont {
    let name = weight == .medium ? "AppleSDGothicNeo-Medium" : "AppleSDGothicNeo-Regular"
    return NSFont(name: name, size: size) ?? NSFont.systemFont(ofSize: size, weight: weight)
}

let ink = NSColor(calibratedRed: 0.118, green: 0.102, blue: 0.090, alpha: 1.0)
let inkSoft = NSColor(calibratedRed: 0.35, green: 0.31, blue: 0.28, alpha: 1.0)
let inkMuted = NSColor(calibratedRed: 0.54, green: 0.50, blue: 0.45, alpha: 1.0)

("패밀리픽  ·  FamilyPick" as NSString).draw(
    at: CGPoint(x: 138, y: 511),
    withAttributes: [.font: sansFont(19, weight: .medium), .foregroundColor: ink]
)

// Quiet hairline rule + overline
cg.setStrokeColor(inkMuted.withAlphaComponent(0.65).cgColor)
cg.setLineWidth(1)
cg.move(to: CGPoint(x: 86, y: 428))
cg.addLine(to: CGPoint(x: 114, y: 428))
cg.strokePath()

("공유 앨범 업로드 전 아이 사진·영상 자동 선별" as NSString).draw(
    at: CGPoint(x: 126, y: 419),
    withAttributes: [.font: sansFont(16), .foregroundColor: inkMuted]
)

// Single-ink Myeongjo editorial headline
("가족에게 건넬 아이 사진," as NSString).draw(
    at: CGPoint(x: 86, y: 338),
    withAttributes: [.font: serifFont(44), .foregroundColor: ink]
)
("내 기준대로 추립니다." as NSString).draw(
    at: CGPoint(x: 86, y: 274),
    withAttributes: [.font: serifFont(44), .foregroundColor: ink]
)

// Hand-sketched vermilion pencil curve under "내 기준대로"
cg.saveGState()
cg.setStrokeColor(NSColor(calibratedRed: 0.76, green: 0.286, blue: 0.212, alpha: 0.85).cgColor)
cg.setLineWidth(2.8)
cg.setLineCap(.round)
cg.move(to: CGPoint(x: 88, y: 268))
cg.addCurve(to: CGPoint(x: 298, y: 270), control1: CGPoint(x: 145, y: 273), control2: CGPoint(x: 235, y: 273))
cg.strokePath()
cg.restoreGState()

// Calm body note
let pStyle = NSMutableParagraphStyle()
pStyle.lineSpacing = 8
("수백 장의 연사 너머, 남기고 싶은 표정만 먼저 골라둡니다.\n모든 사진과 시선 학습은 오직 iPhone 안에서만 다뤄집니다." as NSString).draw(
    in: CGRect(x: 86, y: 156, width: 570, height: 84),
    withAttributes: [.font: sansFont(19), .foregroundColor: inkSoft, .paragraphStyle: pStyle]
)

// Bottom hairline colophon
cg.setStrokeColor(NSColor(calibratedRed: 0.12, green: 0.10, blue: 0.09, alpha: 0.12).cgColor)
cg.move(to: CGPoint(x: 86, y: 120))
cg.addLine(to: CGPoint(x: 610, y: 120))
cg.strokePath()

("Studio Taeo  ·  familypick.studiotaeo.com" as NSString).draw(
    at: CGPoint(x: 86, y: 84),
    withAttributes: [.font: sansFont(15), .foregroundColor: inkMuted]
)

NSGraphicsContext.restoreGraphicsState()

guard let png = rep.representation(using: .png, properties: [:]) else {
    fatalError("Failed to encode PNG")
}
try png.write(to: outURL)
print("Wrote \(outURL.path) (\(png.count) bytes)")
