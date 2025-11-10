import XCTest
@testable import TherapistMe

// HIPAA Compliance: Test encryption service
// Validates AES-256-GCM encryption implementation

final class EncryptionTests: XCTestCase {
    var encryptionService: EncryptionService!
    
    override func setUp() {
        super.setUp()
        encryptionService = EncryptionService.shared
    }
    
    /// HIPAA Test: Verify AES-256 encryption produces different ciphertext
    func testEncryptionProducesDifferentCiphertext() throws {
        let plaintext = "Sensitive PHI data".data(using: .utf8)!
        let encrypted = try encryptionService.encrypt(plaintext, associatedData: nil)
        
        XCTAssertNotEqual(encrypted.ciphertext, plaintext)
        XCTAssertEqual(encrypted.nonce.count, 12)
        XCTAssertEqual(encrypted.tag.count, 16)
    }
    
    /// HIPAA Test: Verify decryption recovers original plaintext
    func testDecryptionRecoversPlaintext() throws {
        let plaintext = "Protected Health Information".data(using: .utf8)!
        let encrypted = try encryptionService.encrypt(plaintext, associatedData: nil)
        let decrypted = try encryptionService.decrypt(encrypted, associatedData: nil)
        
        XCTAssertEqual(decrypted, plaintext)
    }
}
