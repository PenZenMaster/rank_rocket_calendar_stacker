# How to Digitally Sign a PowerShell Script

## 1. Introduction

Digitally signing PowerShell scripts is a crucial security measure that helps ensure the integrity and authenticity of your scripts. When a script is digitally signed, it means that the script has not been tampered with since it was signed, and it originates from a trusted publisher. This is particularly important in environments where PowerShell execution policies are set to restrict unsigned scripts, such as `AllSigned` or `RemoteSigned`.

PowerShell uses Authenticode signatures to verify the integrity of scripts. An Authenticode signature is a digital signature format used by Microsoft to verify the authenticity of software and prevent tampering. When you run a signed script, PowerShell checks the digital signature to confirm that the script has not been altered and that it comes from a trusted source. If the signature is invalid or the script has been modified after signing, PowerShell will prevent the script from running, depending on the configured execution policy.

This guide will walk you through the process of digitally signing PowerShell scripts, covering the necessary prerequisites, methods for obtaining a code signing certificate, the cmdlets used for signing and verification, and important considerations regarding PowerShell execution policies.



## 2. Prerequisites for Signing PowerShell Scripts

Before you can digitally sign a PowerShell script, you need to meet a few prerequisites:

### 2.1. Code Signing Certificate

The most critical prerequisite is a valid code signing certificate. This certificate is used to create the digital signature that will be embedded in your PowerShell script. There are two main types of code signing certificates you can use:

*   **Certificates from a Certificate Authority (CA)**: These are certificates issued by a trusted third-party Certificate Authority (e.g., DigiCert, Sectigo, Entrust). Certificates from a public CA are generally recommended for scripts that will be distributed widely or used in environments where trust in a public CA is established. They provide a higher level of trust because the CA verifies your identity before issuing the certificate.

*   **Self-Signed Certificates**: You can create your own self-signed certificate. These are useful for internal use, testing, or in environments where you control the trust chain (e.g., within an organization's Active Directory where you can distribute the self-signed certificate to trusted root certificate stores). However, self-signed certificates are not inherently trusted by other systems and will typically require manual installation and trust establishment on each machine where the signed script will run.

Regardless of the source, the certificate must have the 


Enhanced Key Usage (EKU) for "Code Signing" (OID 1.3.6.1.5.5.7.3.3).

### 2.2. PowerShell Environment

You need a PowerShell environment (PowerShell 5.1 or PowerShell Core 6.x/7.x and above) with the necessary modules. The `Set-AuthenticodeSignature` cmdlet, which is central to signing scripts, is part of the `Microsoft.PowerShell.Security` module, which is typically available by default in PowerShell environments.

## 3. Obtaining a Code Signing Certificate

### 3.1. From a Certificate Authority (CA)

To obtain a code signing certificate from a commercial CA, you typically follow these steps:

1.  **Choose a CA**: Select a reputable Certificate Authority (e.g., DigiCert, Sectigo, Entrust, GlobalSign). The cost and validation process can vary between CAs.
2.  **Purchase a Certificate**: Go through the purchase process on the CA's website. You will likely need to provide organizational details and undergo a validation process, which can range from simple domain validation to extensive organizational validation, depending on the certificate type.
3.  **Generate a Certificate Signing Request (CSR)**: Some CAs might require you to generate a CSR on your machine. This process creates a private key on your system and a public key component (the CSR) that you submit to the CA. The CA then uses this CSR to issue your certificate.
4.  **Install the Certificate**: Once the CA issues the certificate, you will receive instructions on how to download and install it on your machine. This usually involves importing the `.pfx` or `.p12` file (which contains both the public certificate and your private key) into your Windows Certificate Store (specifically, the `Personal` store for the user or computer account that will perform the signing).

### 3.2. Creating a Self-Signed Certificate

For internal use or testing, you can create a self-signed certificate using PowerShell. Keep in mind that scripts signed with a self-signed certificate will only be trusted on machines where this certificate is explicitly installed in the `Trusted Publishers` certificate store.

Here's how to create a self-signed code signing certificate:

```powershell
# Create a new self-signed certificate
$cert = New-SelfSignedCertificate \
    -Subject "CN=My PowerShell Signing Certificate, OU=IT Department, O=My Company" \
    -Type CodeSigningCert \
    -CertStoreLocation Cert:\CurrentUser\My \
    -KeyUsage DigitalSignature \
    -KeyAlgorithm RSA \
    -KeyLength 2048 \
    -NotAfter (Get-Date).AddYears(1)

# Export the certificate (optional, but recommended for backup or distribution)
# You will be prompted for a password to protect the private key
Export-PfxCertificate -Cert $cert -FilePath "C:\Path\To\Your\SelfSignedCodeSigningCert.pfx"

# To import the certificate on another machine:
# Import-PfxCertificate -FilePath "C:\Path\To\Your\SelfSignedCodeSigningCert.pfx" -CertStoreLocation Cert:\CurrentUser\My
```

**Explanation of parameters for `New-SelfSignedCertificate`:**

*   `-Subject`: Defines the subject name of the certificate. The `CN` (Common Name) is important for identification.
*   `-Type CodeSigningCert`: Specifies that this certificate is intended for code signing.
*   `-CertStoreLocation Cert:\CurrentUser\My`: Specifies the location where the certificate will be stored. `Cert:\CurrentUser\My` refers to the Personal certificate store for the current user.
*   `-KeyUsage DigitalSignature`: Ensures the certificate can be used for digital signatures.
*   `-KeyAlgorithm RSA` and `-KeyLength 2048`: Define the cryptographic algorithm and key length.
*   `-NotAfter (Get-Date).AddYears(1)`: Sets the certificate's expiration date to one year from the current date. Adjust as needed.

After creating the self-signed certificate, it will be available in your `Personal` certificate store. You can view it using the Certificate Manager (certmgr.msc) or by running `Get-ChildItem Cert:\CurrentUser\My` in PowerShell.



## 4. Signing a PowerShell Script

Once you have a code signing certificate installed on your system, you can use the `Set-AuthenticodeSignature` cmdlet to sign your PowerShell scripts. This cmdlet adds an Authenticode signature to a script file.

### 4.1. Identifying Your Certificate

First, you need to identify the certificate you want to use for signing. You can do this by retrieving it from your certificate store. The most common way is to use `Get-ChildItem` in the `Cert:` drive.

```powershell
# Get the certificate by its subject name (Common Name)
$cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Where-Object {$_.Subject -like "*My PowerShell Signing Certificate*"}

# If you have multiple certificates, you might need to be more specific or select interactively
# $cert = Get-ChildItem -Path Cert:\CurrentUser\My -CodeSigningCert | Out-GridView -PassThru

# Verify that a certificate was found
if ($cert -eq $null) {
    Write-Error "No code signing certificate found. Please ensure you have a valid certificate installed."
    exit
}
```

**Note**: The `-CodeSigningCert` parameter with `Get-ChildItem` is crucial as it filters for certificates that have the Code Signing Enhanced Key Usage and contain a private key, which is necessary for signing.

### 4.2. Applying the Signature

With your certificate identified, you can now sign your script using `Set-AuthenticodeSignature`.

```powershell
# Define the path to your PowerShell script
$scriptPath = "C:\Path\To\Your\MyScript.ps1"

# Sign the script
Set-AuthenticodeSignature -FilePath $scriptPath -Certificate $cert

# You can also add a timestamp server for long-term validity (recommended)
# A timestamp server ensures that the signature remains valid even after the certificate expires
# Set-AuthenticodeSignature -FilePath $scriptPath -Certificate $cert -TimestampServer "http://timestamp.digicert.com"

Write-Host "Script '$scriptPath' signed successfully."
```

**Explanation of parameters for `Set-AuthenticodeSignature`:**

*   `-FilePath`: Specifies the path to the PowerShell script file you want to sign.
*   `-Certificate`: Specifies the code signing certificate object obtained in the previous step.
*   `-TimestampServer` (Optional, but Recommended): Specifies the URL of a timestamp server. Using a timestamp server ensures that the signature remains valid even after the signing certificate expires, as long as the timestamp was applied while the certificate was still valid. This is known as long-term validation (LTV).

After running this command, a digital signature block will be appended to the end of your PowerShell script file. It will look something like this:

```powershell
# SIG # Begin signature block
# MII... (long string of characters)
# SIG # End signature block
```

**Important**: Do not manually edit the script after it has been signed. Any modification to the script, even a single character, will invalidate the digital signature, and PowerShell will treat the script as unsigned or tampered with.

## 5. Verifying a PowerShell Script Signature

To verify the digital signature of a PowerShell script, you can use the `Get-AuthenticodeSignature` cmdlet. This cmdlet retrieves information about the Authenticode signature in a file.

```powershell
# Define the path to your signed PowerShell script
$scriptPath = "C:\Path\To\Your\MyScript.ps1"

# Get the signature information
$signature = Get-AuthenticodeSignature -FilePath $scriptPath

# Display the signature status
Write-Host "Signature Status: $($signature.Status)"
Write-Host "Signer: $($signature.SignerCertificate.Subject)"
Write-Host "Hash Algorithm: $($signature.HashAlgorithm)"
Write-Host "TimeStamper: $($signature.TimeStamperCertificate.Subject)"

# Check if the signature is valid
if ($signature.Status -eq "Valid") {
    Write-Host "The script is digitally signed and the signature is valid."
} else {
    Write-Host "The script is not validly signed or has been tampered with. Status: $($signature.Status)"
}
```

**Possible `Status` values from `Get-AuthenticodeSignature`:**

*   `Valid`: The signature is valid, and the script has not been tampered with.
*   `NotSigned`: The file is not signed.
*   `HashMismatch`: The file has been modified after signing.
*   `NotTrusted`: The signing certificate is not trusted on the local system.
*   `UnknownError`: An unexpected error occurred during verification.

## 6. PowerShell Execution Policies

PowerShell execution policies are security features that control the conditions under which PowerShell loads configuration files and runs scripts. Understanding these policies is crucial when working with signed scripts.

You can view the current execution policy using `Get-ExecutionPolicy` and set it using `Set-ExecutionPolicy`.

```powershell
# Get the current execution policy
Get-ExecutionPolicy

# Set the execution policy (requires administrative privileges)
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Here are the common execution policies and how they relate to signed scripts:

*   **`Restricted`**: (Default for Windows client computers) No scripts can run. PowerShell can be used only in interactive mode.

*   **`AllSigned`**: All scripts must be digitally signed by a trusted publisher, including scripts that you write on the local computer. If you try to run an unsigned script, or a script that is signed by a publisher that you have not yet trusted, PowerShell will block it. If a signed script has been tampered with, PowerShell will also block it.

*   **`RemoteSigned`**: (Default for Windows server computers) Scripts created on the local computer do not require a digital signature. Scripts downloaded from the internet (including email and instant messaging programs) must be digitally signed by a trusted publisher. This policy helps prevent running malicious scripts downloaded from the internet.

*   **`Unrestricted`**: All scripts can run. This policy is generally not recommended for security reasons as it allows all scripts, regardless of their source or signature, to run.

*   **`Bypass`**: Nothing is blocked and no warnings or prompts are given. This policy is designed for configurations in which a PowerShell script is built into a larger application or for configurations in which PowerShell is the foundation for a program that has its own security model.

*   **`Undefined`**: No execution policy is set for the current scope. If the execution policy in all scopes is `Undefined`, the effective execution policy is `Restricted`.

For signed scripts to run, the execution policy must be `AllSigned` or `RemoteSigned` (for remote scripts). If you are using a self-signed certificate, you must ensure that the certificate is installed in the `Trusted Publishers` certificate store on any machine where you intend to run the signed script. Otherwise, even with `AllSigned` or `RemoteSigned`, the script will be blocked because the publisher is not trusted.

