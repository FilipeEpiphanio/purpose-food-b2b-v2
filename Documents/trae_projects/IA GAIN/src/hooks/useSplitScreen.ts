import { useState, useEffect } from "react";

export const useSplitScreen = () => {
  const [isSplitScreen, setIsSplitScreen] = useState(false);
  const [screenWidth, setScreenWidth] = useState(window.innerWidth);

  useEffect(() => {
    const checkScreenSize = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      setScreenWidth(width);
      
      // Detectar tela dividida: largura entre 768px e 1280px
      // ou quando a proporção width/height indica uma janela dividida
      const isSplit = width < 1280 && width >= 768;
      
      if (isSplit !== isSplitScreen) {
        console.log(` Detecção de tela: ${width}x${height}, Split: ${isSplit}`);
        setIsSplitScreen(isSplit);
      }
    };

    // Verificar no mount
    checkScreenSize();
    
    // Adicionar listeners
    window.addEventListener("resize", checkScreenSize);
    window.addEventListener("orientationchange", checkScreenSize);
    
    // Verificar periodicamente (para casos de drag resize)
    const interval = setInterval(checkScreenSize, 500);

    return () => {
      window.removeEventListener("resize", checkScreenSize);
      window.removeEventListener("orientationchange", checkScreenSize);
      clearInterval(interval);
    };
  }, [isSplitScreen]);

  return { isSplitScreen, screenWidth };
};
