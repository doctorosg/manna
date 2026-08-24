import AVFoundation
import Combine

final class SoundManager {
    static let shared = SoundManager()
    private let engine = AVAudioEngine()
    private let tonePlayer = AVAudioPlayerNode()
    private let format = AVAudioFormat(standardFormatWithSampleRate: 44_100, channels: 1)!
    @Published var isMuted: Bool = UserDefaults.standard.bool(forKey: "manna_muted")

    private init() {
        engine.attach(tonePlayer)
        engine.connect(tonePlayer, to: engine.mainMixerNode, format: format)
    }

    func toggleMute() {
        setMuted(!isMuted)
    }

    func setMuted(_ muted: Bool) {
        isMuted = muted
        UserDefaults.standard.set(muted, forKey: "manna_muted")
    }

    func playCorrect() { playTones([660, 880]) }
    func playWrong() { playTones([220, 165]) }
    func playWagerWin() { playTones([523, 659, 784]) }

    private func playTones(_ frequencies: [Double]) {
        guard !isMuted else { return }
        do {
            try AVAudioSession.sharedInstance().setCategory(.ambient, mode: .default)
            try AVAudioSession.sharedInstance().setActive(true)
            tonePlayer.stop()
            if !engine.isRunning { try engine.start() }
            frequencies.forEach { tonePlayer.scheduleBuffer(toneBuffer(frequency: $0)) }
            tonePlayer.play()
        } catch {
            print("Sound error: \(error)")
        }
    }

    private func toneBuffer(frequency: Double, duration: Double = 0.14) -> AVAudioPCMBuffer {
        let frameCount = AVAudioFrameCount(format.sampleRate * duration)
        let buffer = AVAudioPCMBuffer(pcmFormat: format, frameCapacity: frameCount)!
        buffer.frameLength = frameCount
        let samples = buffer.floatChannelData![0]
        for frame in 0..<Int(frameCount) {
            let progress = Double(frame) / Double(frameCount)
            let envelope = min(progress * 12, (1 - progress) * 12, 1)
            samples[frame] = Float(sin(2 * .pi * frequency * Double(frame) / format.sampleRate) * 0.22 * envelope)
        }
        return buffer
    }
}
