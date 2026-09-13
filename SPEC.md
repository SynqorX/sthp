# CadenceType - Technical Specification

## 1. Executive Summary & Objective

**CadenceType** is a cross-platform desktop daemon designed for automated text entry, end-to-end user-flow benchmarking, and accessibility assistance. 

Its primary purpose is to inject text into active system windows using realistic human typing dynamics (stochastic keystroke timing, non-uniform pauses, and typographical error corrections) rather than instantaneous buffer transfers. This makes it ideal for testing text-input resilience in modern canvas-based editors, streaming input stress tests, and automated UI demonstrations.

---

## 2. Technical Architecture & Constraints

### Why Clipboard Pasting / Synthetic DOM Events Fall Short
* **Canvas-Based Rendering Layers:** Modern rich-text editors (e.g., Google Docs, Canva, Figma) frequently bypass native browser `<textarea>` or `contenteditable` nodes. They utilize custom canvas rendering coupled with hidden offscreen focus targets.
* **Untrusted Synthetic Events:** JavaScript events dispatched within the webpage context (`element.dispatchEvent(new KeyboardEvent(...))`) carry an immutable `isTrusted: false` flag. Canvas engines and complex event loops frequently ignore or drop these events to prevent cross-site scripting (XSS) and erratic cursor states.
* **Buffer Flooding:** Pasting massive blocks of text tests only large buffer allocations; it does not benchmark how streaming input processors, Operational Transformation (OT) handlers, or real-time auto-completion plugins handle continuous interactive workloads.

### Solution: OS-Level Input Synthesis
CadenceType operates at the operating system's native hardware input layer:
1. Dispatches platform-native virtual scan codes (`VK_PACKET` on Windows, `CGEvent` on macOS, `uinput` on Linux) using Python's `pynput` interface.
2. Because events originate from the operating system event queue, consumer applications and web browsers receive them as legitimate, hardware-level user input (`isTrusted: true`).
3. The system functions uniformly across desktop applications, terminal emulators, and browser environments.

---

## 3. Directory Architecture & Component Responsibilities

```plaintext
cadence_type/
├── main.py              # Application lifecycle, threading, and global panic listener
├── gui.py               # Parameter control panel & setup countdown
├── engine.py            # Event loop, cadence algorithms, and input dispatcher
├── keyboard_map.py      # Spatial neighbor layout matrix for typographical variance
├── requirements.txt     # Dependency definitions
└── SPEC.md              # Technical specification
