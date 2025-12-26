"""
Command Palette Component for btc-market-regime Dashboard

Implements Cmd+K keyboard shortcut to open a command palette for:
- Instant market switching
- Quick navigation
- Command execution

Design: Bloomberg Terminal style with dark glassmorphism
"""

import streamlit as st


def inject_command_palette():
    """Injects Command Palette with Cmd+K keyboard shortcut via st.html()."""
    
    st.html("""
        <style>
        /* Command Palette Overlay */
        .command-palette-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(8px);
            z-index: 10000;
            align-items: flex-start;
            justify-content: center;
            padding-top: 20vh;
        }
        
        .command-palette-overlay.active {
            display: flex;
        }
        
        /* Command Palette Container */
        .command-palette {
            width: 600px;
            max-width: 90vw;
            background: rgba(11, 12, 16, 0.95);
            border: 1px solid #05D9E8;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(5, 217, 232, 0.3);
            overflow: hidden;
        }
        
        /* Search Input */
        .command-palette-input {
            width: 100%;
            padding: 1rem 1.5rem;
            background: rgba(31, 40, 51, 0.6);
            border: none;
            border-bottom: 1px solid rgba(69, 162, 158, 0.3);
            color: white;
            font-family: 'Inter', sans-serif;
            font-size: 1.1rem;
            outline: none;
        }
        
        .command-palette-input::placeholder {
            color: rgba(255, 255, 255, 0.4);
        }
        
        /* Command List */
        .command-list {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .command-item {
            padding: 0.75rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            cursor: pointer;
            transition: background 0.15s ease-out;
            border-left: 3px solid transparent;
        }
        
        .command-item:hover,
        .command-item.selected {
            background: rgba(5, 217, 232, 0.1);
            border-left-color: #05D9E8;
        }
        
        .command-icon {
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
        }
        
        .command-title {
            flex: 1;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            color: rgba(255, 255, 255, 0.9);
        }
        
        .command-shortcut {
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.5);
            background: rgba(255, 255, 255, 0.1);
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
        }
        
        /* Empty State */
        .command-empty {
            padding: 3rem 1.5rem;
            text-align: center;
            color: rgba(255, 255, 255, 0.4);
            font-family: 'Inter', sans-serif;
        }
        </style>
        
        <div class="command-palette-overlay" id="commandPaletteOverlay">
            <div class="command-palette">
                <input 
                    type="text" 
                    class="command-palette-input" 
                    id="commandPaletteInput"
                    placeholder="Type a command or search..."
                    autocomplete="off"
                />
                <div class="command-list" id="commandList">
                    <!-- Commands will be injected here -->
                </div>
            </div>
        </div>
        
        <script>
        (function() {
            const overlay = document.getElementById('commandPaletteOverlay');
            const input = document.getElementById('commandPaletteInput');
            const commandList = document.getElementById('commandList');
            
            // Command definitions
            const commands = [
                { id: 'switch-btc', title: 'Switch to Bitcoin (BTC)', icon: '₿', action: 'market:BTC' },
                { id: 'switch-eth', title: 'Switch to Ethereum (ETH)', icon: 'Ξ', action: 'market:ETH' },
                { id: 'switch-sol', title: 'Switch to Solana (SOL)', icon: '◎', action: 'market:SOL' },
                { id: 'refresh', title: 'Refresh Intelligence', icon: '⟳', shortcut: 'R', action: 'refresh' },
                { id: 'backtest', title: 'Run Backtest', icon: '🧪', action: 'backtest' },
                { id: 'optimize', title: 'Optimize Weights', icon: '⚙️', action: 'optimize' },
            ];
            
            let selectedIndex = 0;
            let filteredCommands = [...commands];
            
            // Render commands
            function renderCommands(filter = '') {
                filteredCommands = commands.filter(cmd => 
                    cmd.title.toLowerCase().includes(filter.toLowerCase())
                );
                
                if (filteredCommands.length === 0) {
                    commandList.innerHTML = '<div class="command-empty">No commands found</div>';
                    return;
                }
                
                commandList.innerHTML = filteredCommands.map((cmd, index) => `
                    <div class="command-item ${index === selectedIndex ? 'selected' : ''}" data-index="${index}">
                        <div class="command-icon">${cmd.icon}</div>
                        <div class="command-title">${cmd.title}</div>
                        ${cmd.shortcut ? `<div class="command-shortcut">${cmd.shortcut}</div>` : ''}
                    </div>
                `).join('');
                
                // Add click handlers
                document.querySelectorAll('.command-item').forEach((item, index) => {
                    item.addEventListener('click', () => executeCommand(index));
                });
            }
            
            // Execute command
            function executeCommand(index) {
                const cmd = filteredCommands[index];
                if (!cmd) return;
                
                // Close palette
                closeCommandPalette();
                
                // Execute action
                if (cmd.action.startsWith('market:')) {
                    const market = cmd.action.split(':')[1];
                    // Trigger Streamlit rerun with market parameter
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        key: 'selected_market',
                        value: market
                    }, '*');
                } else if (cmd.action === 'refresh') {
                    window.location.reload();
                } else if (cmd.action === 'backtest' || cmd.action === 'optimize') {
                    // Trigger specific action via session state
                    window.parent.postMessage({
                        type: 'streamlit:setComponentValue',
                        key: 'command_action',
                        value: cmd.action
                    }, '*');
                }
            }
            
            // Open command palette
            function openCommandPalette() {
                overlay.classList.add('active');
                input.value = '';
                input.focus();
                selectedIndex = 0;
                renderCommands();
            }
            
            // Close command palette
            function closeCommandPalette() {
                overlay.classList.remove('active');
            }
            
            // Keyboard shortcuts
            document.addEventListener('keydown', (e) => {
                // Cmd+K or Ctrl+K to open
                if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                    e.preventDefault();
                    openCommandPalette();
                }
                
                // ESC to close
                if (e.key === 'Escape') {
                    closeCommandPalette();
                }
                
                // Navigation when palette is open
                if (overlay.classList.contains('active')) {
                    if (e.key === 'ArrowDown') {
                        e.preventDefault();
                        selectedIndex = (selectedIndex + 1) % filteredCommands.length;
                        renderCommands(input.value);
                    } else if (e.key === 'ArrowUp') {
                        e.preventDefault();
                        selectedIndex = (selectedIndex - 1 + filteredCommands.length) % filteredCommands.length;
                        renderCommands(input.value);
                    } else if (e.key === 'Enter') {
                        e.preventDefault();
                        executeCommand(selectedIndex);
                    }
                }
            });
            
            // Search filter
            input.addEventListener('input', (e) => {
                selectedIndex = 0;
                renderCommands(e.target.value);
            });
            
            // Click outside to close
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    closeCommandPalette();
                }
            });
            
            // Initial render
            renderCommands();
        })();
        </script>
    """)
