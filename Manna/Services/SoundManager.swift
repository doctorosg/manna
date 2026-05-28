import AVFoundation

class SoundManager {
    static let shared = SoundManager()
    private var player: AVAudioPlayer?
    @Published var isMuted: Bool = UserDefaults.standard.bool(forKey: "manna_muted")

    func toggleMute() {
        isMuted.toggle()
        UserDefaults.standard.set(isMuted, forKey: "manna_muted")
    }

    func playCorrect() { playSound("correct") }
    func playWrong() { playSound("wrong") }
    func playWagerWin() { playSound("wager_win") }

    private func playSound(_ name: String) {
        guard !isMuted else { return }
        guard let url = Bundle.main.url(forResource: name, withExtension: "mp3") ?? Bundle.main.url(forResource: name, withExtension: "wav") else { return }
        do {
            player = try AVAudioPlayer(contentsOf: url)
            player?.play()
        } catch {
            print("Sound error: \(error)")
        }
    }
}
