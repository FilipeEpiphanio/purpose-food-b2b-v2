#!/usr/bin/env python3
"""
Advanced Momentum Analysis Runner
Executes comprehensive momentum analysis on specified symbols
"""

import asyncio
import logging
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional

# Add src to path
sys.path.append(str(Path(__file__).parent / 'src'))

from analysis.momentum_analyzer import AdvancedMomentumAnalyzer
from utils.config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/momentum_analysis.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MomentumAnalysisRunner:
    """Runner for advanced momentum analysis"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config = ConfigManager(config_path)
        self.analyzer = AdvancedMomentumAnalyzer()
        self.results = {}
        
    async def analyze_symbol(self, symbol: str, timeframe: str = 'H1') -> Dict:
        """Analyze momentum for a single symbol"""
        try:
            logger.info(f"Analyzing momentum for {symbol} on {timeframe}")
            
            # Calculate momentum indicators
            momentum_data = await self.analyzer.calculate_comprehensive_momentum(symbol, timeframe)
            
            # Detect divergences
            divergences = self.analyzer.detect_rsi_divergence(symbol, timeframe)
            
            # Generate trading signals
            signals = await self.analyzer.generate_trading_signals(symbol, timeframe)
            
            # Calculate confidence and targets
            confidence = self.analyzer.calculate_confidence(momentum_data)
            price_targets = self.analyzer.calculate_price_targets(symbol, momentum_data)
            stop_loss = self.analyzer.calculate_stop_loss(symbol, momentum_data)
            
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat(),
                'momentum_indicators': momentum_data,
                'divergences': divergences,
                'signals': signals,
                'confidence': confidence,
                'price_targets': price_targets,
                'stop_loss': stop_loss,
                'time_horizon': self.analyzer.determine_time_horizon(momentum_data),
                'risk_level': self.analyzer.determine_risk_level(momentum_data)
            }
            
            logger.info(f"Momentum analysis completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing momentum for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}
    
    async def analyze_multiple_symbols(self, symbols: List[str], timeframe: str = 'H1') -> Dict:
        """Analyze momentum for multiple symbols"""
        logger.info(f"Analyzing momentum for {len(symbols)} symbols")
        
        tasks = [self.analyze_symbol(symbol, timeframe) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        return {
            'analysis_type': 'momentum',
            'symbols': symbols,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'results': results
        }
    
    async def scan_for_opportunities(self, symbols: List[str], min_confidence: float = 0.7) -> Dict:
        """Scan for momentum trading opportunities"""
        logger.info(f"Scanning for momentum opportunities with min confidence {min_confidence}")
        
        # Analyze all symbols
        analysis_results = await self.analyze_multiple_symbols(symbols)
        
        # Filter high-confidence opportunities
        opportunities = []
        for result in analysis_results['results']:
            if 'error' not in result and result.get('confidence', 0) >= min_confidence:
                opportunities.append(result)
        
        # Sort by confidence
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'scan_type': 'momentum_opportunities',
            'min_confidence': min_confidence,
            'total_symbols': len(symbols),
            'opportunities_found': len(opportunities),
            'timestamp': datetime.now().isoformat(),
            'top_opportunities': opportunities[:10]  # Top 10 opportunities
        }
    
    async def generate_momentum_heatmap(self, symbols: List[str], timeframe: str = 'H1') -> Dict:
        """Generate momentum heatmap for multiple symbols"""
        logger.info(f"Generating momentum heatmap for {len(symbols)} symbols")
        
        heatmap_data = await self.analyzer.generate_momentum_heatmap(symbols, timeframe)
        
        return {
            'heatmap_type': 'momentum',
            'symbols': symbols,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'heatmap_data': heatmap_data
        }
    
    def save_results(self, results: Dict, filename: str = None) -> str:
        """Save analysis results to file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reports/momentum_analysis_{timestamp}.json"
        
        # Ensure reports directory exists
        Path('reports').mkdir(exist_ok=True)
        
        # Save results
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Results saved to {filename}")
        return filename
    
    def print_results_summary(self, results: Dict):
        """Print summary of analysis results"""
        print("\n" + "="*60)
        print("MOMENTUM ANALYSIS RESULTS")
        print("="*60)
        print(f"Analysis Type: {results.get('analysis_type', 'N/A')}")
        print(f"Timeframe: {results.get('timeframe', 'N/A')}")
        print(f"Timestamp: {results.get('timestamp', 'N/A')}")
        print(f"Symbols Analyzed: {len(results.get('symbols', []))}")
        print("-"*60)
        
        for result in results.get('results', []):
            if 'error' in result:
                print(f"\n❌ {result['symbol']}: ERROR - {result['error']}")
                continue
            
            print(f"\n📊 {result['symbol']}:")
            print(f"   Confidence: {result['confidence']:.2%}")
            print(f"   Time Horizon: {result['time_horizon']}")
            print(f"   Risk Level: {result['risk_level']}")
            
            if result['signals']:
                for signal in result['signals']:
                    signal_type = signal.get('signal', 'N/A')
                    strength = signal.get('strength', 0)
                    print(f"   Signal: {signal_type} (Strength: {strength:.2f})")
            
            if result['price_targets']:
                targets = result['price_targets']
                print(f"   Targets: Entry: {targets.get('entry', 'N/A')}, TP: {targets.get('take_profit', 'N/A')}, SL: {targets.get('stop_loss', 'N/A')}")
            
            if result['divergences']:
                print(f"   Divergences: {len(result['divergences'])} detected")
        
        print("\n" + "="*60)
    
    async def run_analysis(self, symbols: List[str], timeframe: str = 'H1', 
                          save_results: bool = True, min_confidence: float = 0.0) -> Dict:
        """Run complete momentum analysis"""
        logger.info(f"Starting momentum analysis for {symbols} on {timeframe}")
        
        # Run analysis
        results = await self.analyze_multiple_symbols(symbols, timeframe)
        
        # Scan for opportunities if confidence threshold is set
        if min_confidence > 0:
            opportunities = await self.scan_for_opportunities(symbols, min_confidence)
            results['opportunities'] = opportunities
        
        # Save results
        if save_results:
            filename = self.save_results(results)
            results['saved_file'] = filename
        
        # Print summary
        self.print_results_summary(results)
        
        return results

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Advanced Momentum Analysis Runner')
    parser.add_argument('--symbols', nargs='+', default=['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD', 'XAUUSD'],
                       help='Symbols to analyze')
    parser.add_argument('--timeframe', default='H1', help='Timeframe for analysis')
    parser.add_argument('--confidence', type=float, default=0.7, help='Minimum confidence for opportunities')
    parser.add_argument('--scan-opportunities', action='store_true', help='Scan for trading opportunities')
    parser.add_argument('--heatmap', action='store_true', help='Generate momentum heatmap')
    parser.add_argument('--save', action='store_true', help='Save results to file')
    parser.add_argument('--output', help='Output filename for results')
    
    args = parser.parse_args()
    
    # Create runner
    runner = MomentumAnalysisRunner()
    
    try:
        if args.heatmap:
            # Generate heatmap
            results = await runner.generate_momentum_heatmap(args.symbols, args.timeframe)
            if args.save:
                filename = runner.save_results(results, args.output)
                print(f"Heatmap saved to: {filename}")
        
        elif args.scan_opportunities:
            # Scan for opportunities
            results = await runner.scan_for_opportunities(args.symbols, args.confidence)
            if args.save:
                filename = runner.save_results(results, args.output)
                print(f"Opportunity scan saved to: {filename}")
        
        else:
            # Run full analysis
            results = await runner.run_analysis(
                symbols=args.symbols,
                timeframe=args.timeframe,
                save_results=args.save,
                min_confidence=args.confidence
            )
            
            if args.save and 'saved_file' in results:
                print(f"Analysis saved to: {results['saved_file']}")
    
    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Momentum analysis stopped by user")
    except Exception as e:
        logger.error(f"Momentum analysis error: {e}")
        sys.exit(1)