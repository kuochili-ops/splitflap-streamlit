    async function smartUpdate(id, target, isInitial = false) {
        // 1. 強制轉換為字串，確保 '0' 不會遺失
        const tStr = (target === undefined || target === null) ? " " : String(target).toUpperCase();
        
        if (memory[id] === tStr || isBusy[id]) return;
        isBusy[id] = true;
        
        let oldStr = (memory[id] === undefined) ? " " : String(memory[id]);
        
        // 2. 針對 0-9 數字的滾動邏輯進行修正
        if (/^[0-9]$/.test(tStr)) {
            let curN = /^[0-9]$/.test(oldStr) ? parseInt(oldStr) : 0;
            let tarN = parseInt(tStr);
            
            // 修正點：使用 do...while 或明確判斷，確保 0 也能被處理
            while (String(curN) !== tStr) {
                let prev = String(curN);
                curN = (curN + 1) % 10;
                performFlip(id, String(curN), prev);
                await new Promise(r => setTimeout(r, baseSpeed * 0.8));
            }
        } 
        else {
            // ... 文字處理邏輯保持不變 ...
            const steps = isInitial ? 8 : 4; 
            for (let i = 0; i < steps; i++) {
                let randChar = charPool.length > 0 ? charPool[Math.floor(Math.random() * charPool.length)] : "X";
                performFlip(id, randChar, oldStr);
                oldStr = randChar;
                await new Promise(r => setTimeout(r, baseSpeed));
            }
            performFlip(id, tStr, oldStr);
        }
        
        memory[id] = tStr; 
        isBusy[id] = false;
    }
