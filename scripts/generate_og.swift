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

// Warm sunlit ivory background
let bgColors = [
    NSColor(calibratedRed: 1.00, green: 0.985, blue: 0.973, alpha: 1.0).cgColor,
    NSColor(calibratedRed: 0.992, green: 0.949, blue: 0.925, alpha: 1.0).cgColor
] as CFArray
let space = CGColorSpaceCreateDeviceRGB()
if let grad = CGGradient(colorsSpace: space, colors: bgColors, locations: [0.0, 1.0]) {
    cg.drawLinearGradient(grad, start: CGPoint(x: 0, y: CGFloat(height)), end: CGPoint(x: CGFloat(width), y: 0), options: [])
}

// Soft sunlit peach radial glow on right
let glowColors = [
    NSColor(calibratedRed: 0.96, green: 0.68, blue: 0.58, alpha: 0.30).cgColor,
    NSColor(calibratedRed: 0.99, green: 0.88, blue: 0.80, alpha: 0.0).cgColor
] as CFArray
if let glow = CGGradient(colorsSpace: space, colors: glowColors, locations: [0.0, 1.0]) {
    cg.drawRadialGradient(
        glow,
        startCenter: CGPoint(x: 930, y: 315),
        startRadius: 20,
        endCenter: CGPoint(x: 930, y: 315),
        endRadius: 340,
        options: []
    )
}

func drawRoundedImage(_ url: URL, in rect: CGRect, radius: CGFloat, border: NSColor? = nil, borderWidth: CGFloat = 0, shadowAlpha: CGFloat = 0.16) {
    guard let img = NSImage(contentsOf: url) else { return }
    cg.saveGState()
    if shadowAlpha > 0 {
        cg.setShadow(offset: CGSize(width: 0, height: -12), blur: 28, color: NSColor(calibratedRed: 0.36, green: 0.18, blue: 0.12, alpha: shadowAlpha).cgColor)
    }
    let outerPath = NSBezierPath(roundedRect: rect, xRadius: radius, yRadius: radius)
    NSColor.white.setFill()
    outerPath.fill()
    cg.restoreGState()

    cg.saveGState()
    outerPath.addClip()
    img.draw(in: rect, from: .zero, operation: .sourceOver, fraction: 1.0)
    cg.restoreGState()

    if let border = border, borderWidth > 0 {
        cg.saveGState()
        border.setStroke()
        outerPath.lineWidth = borderWidth
        outerPath.stroke()
        cg.restoreGState()
    }
}

func drawPolaroid(_ url: URL, center: CGPoint, size: CGFloat, angleDeg: CGFloat) {
    guard let img = NSImage(contentsOf: url) else { return }
    cg.saveGState()
    cg.translateBy(x: center.x, y: center.y)
    cg.rotate(by: angleDeg * .pi / 180.0)

    let cardRect = CGRect(x: -size / 2 - 10, y: -size / 2 - 14, width: size + 20, height: size + 24)
    cg.saveGState()
    cg.setShadow(offset: CGSize(width: 0, height: -10), blur: 24, color: NSColor(calibratedRed: 0.34, green: 0.17, blue: 0.11, alpha: 0.18).cgColor)
    let cardPath = NSBezierPath(roundedRect: cardRect, xRadius: 20, yRadius: 20)
    NSColor.white.setFill()
    cardPath.fill()
    cg.restoreGState()

    let imgRect = CGRect(x: -size / 2, y: -size / 2 + 2, width: size, height: size)
    cg.saveGState()
    let clip = NSBezierPath(roundedRect: imgRect, xRadius: 13, yRadius: 13)
    clip.addClip()
    img.draw(in: imgRect, from: .zero, operation: .sourceOver, fraction: 1.0)
    cg.restoreGState()

    NSColor(calibratedRed: 0.43, green: 0.28, blue: 0.21, alpha: 0.10).setStroke()
    cardPath.lineWidth = 1
    cardPath.stroke()
    cg.restoreGState()
}

// Right side composition: 2 warm floating prints + Build 13 phone centerpiece
drawPolaroid(photo1URL, center: CGPoint(x: 785, y: 215), size: 148, angleDeg: 7.0)
drawPolaroid(photo2URL, center: CGPoint(x: 1075, y: 405), size: 136, angleDeg: -6.5)

// Warm pearl phone bezel
let phoneW: CGFloat = 246
let phoneH: CGFloat = 534
let phoneRect = CGRect(x: 930 - phoneW / 2, y: (CGFloat(height) - phoneH) / 2, width: phoneW, height: phoneH)
cg.saveGState()
cg.setShadow(offset: CGSize(width: 0, height: -18), blur: 40, color: NSColor(calibratedRed: 0.34, green: 0.17, blue: 0.11, alpha: 0.24).cgColor)
let bezelRect = phoneRect.insetBy(dx: -8, dy: -8)
let bezelPath = NSBezierPath(roundedRect: bezelRect, xRadius: 38, yRadius: 38)
NSColor(calibratedRed: 0.957, green: 0.925, blue: 0.902, alpha: 1.0).setFill()
bezelPath.fill()
cg.restoreGState()

drawRoundedImage(phoneURL, in: phoneRect, radius: 30, border: NSColor(calibratedRed: 0.43, green: 0.28, blue: 0.21, alpha: 0.14), borderWidth: 1, shadowAlpha: 0)

// Left side brand & editorial copy
drawRoundedImage(iconURL, in: CGRect(x: 84, y: 468, width: 68, height: 68), radius: 17, shadowAlpha: 0.20)

func font(_ size: CGFloat, weight: NSFont.Weight) -> NSFont {
    return NSFont(name: "AppleSDGothicNeo-Bold", size: size) ?? NSFont.systemFont(ofSize: size, weight: weight)
}
func regFont(_ size: CGFloat) -> NSFont {
    return NSFont(name: "AppleSDGothicNeo-Medium", size: size) ?? NSFont.systemFont(ofSize: size, weight: .medium)
}

let brandAttrs: [NSAttributedString.Key: Any] = [
    .font: font(24, weight: .bold),
    .foregroundColor: NSColor(calibratedRed: 0.14, green: 0.11, blue: 0.10, alpha: 1.0)
]
("패밀리픽 · FamilyPick" as NSString).draw(at: CGPoint(x: 168, y: 486), withAttributes: brandAttrs)

// Headline line 1
let h1Attrs: [NSAttributedString.Key: Any] = [
    .font: font(46, weight: .bold),
    .foregroundColor: NSColor(calibratedRed: 0.14, green: 0.11, blue: 0.10, alpha: 1.0)
]
("올릴 만한 아이 사진만," as NSString).draw(at: CGPoint(x: 84, y: 360), withAttributes: h1Attrs)

// Headline line 2 (Coral)
let h2Attrs: [NSAttributedString.Key: Any] = [
    .font: font(46, weight: .bold),
    .foregroundColor: NSColor(calibratedRed: 0.85, green: 0.30, blue: 0.23, alpha: 1.0)
]
("내 기준으로 쏙." as NSString).draw(at: CGPoint(x: 84, y: 298), withAttributes: h2Attrs)

// Warm subtitle
let subStyle = NSMutableParagraphStyle()
subStyle.lineSpacing = 6
let subAttrs: [NSAttributedString.Key: Any] = [
    .font: regFont(21),
    .foregroundColor: NSColor(calibratedRed: 0.39, green: 0.34, blue: 0.31, alpha: 1.0),
    .paragraphStyle: subStyle
]
("체크(✓)할수록 우리 집 기준을 배우는 다정한 사진 선별.\n100% 온디바이스 AI · 사진 서버 전송 0장" as NSString)
    .draw(in: CGRect(x: 84, y: 178, width: 580, height: 84), withAttributes: subAttrs)

// Soft pill at bottom left
let pillRect = CGRect(x: 84, y: 92, width: 326, height: 40)
let pillPath = NSBezierPath(roundedRect: pillRect, xRadius: 20, yRadius: 20)
NSColor(calibratedRed: 0.992, green: 0.925, blue: 0.906, alpha: 1.0).setFill()
pillPath.fill()

let pillAttrs: [NSAttributedString.Key: Any] = [
    .font: regFont(16),
    .foregroundColor: NSColor(calibratedRed: 0.74, green: 0.23, blue: 0.16, alpha: 1.0)
]
("패밀리앨범 · 가족 공유를 위한 iPhone 앱" as NSString).draw(at: CGPoint(x: 106, y: 101), withAttributes: pillAttrs)

NSGraphicsContext.restoreGraphicsState()

guard let png = rep.representation(using: .png, properties: [:]) else {
    fatalError("Failed to encode PNG")
}
try png.write(to: outURL)
print("Wrote \(outURL.path) (\(png.count) bytes)")
