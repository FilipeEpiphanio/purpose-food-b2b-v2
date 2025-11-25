#!/usr/bin/env python3
"""
Advanced Pattern Recognition Runner
Executes comprehensive pattern recognition analysis on specified symbols
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

from analysis.pattern_recognition import AdvancedPatternRecognition
from utils.config_manager import ConfigManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/pattern_recognition.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PatternRecognitionRunner:
    """Runner for advanced pattern recognition analysis"""
    
    def __init__(self, config_path: str = 'config.json'):
        self.config = ConfigManager(config_path)
        self.recognizer = AdvancedPatternRecognition()
        self.results = {}
        
    async def analyze_symbol(self, symbol: str, timeframe: str = 'H1') -> Dict:
        """Analyze patterns for a single symbol"""
        try:
            logger.info(f"Analyzing patterns for {symbol} on {timeframe}")
            
            # Train ML model if not already trained
            if not self.recognizer.model_trained:
                logger.info("Training ML pattern recognition model...")
                await self.recognizer.train_ml_model()
            
            # Detect trend lines
            trend_lines = await self.recognizer.detect_trend_lines(symbol, timeframe)
            
            # Detect various patterns
            patterns = {}
            patterns['triangles'] = await self.recognizer.detect_triangles(symbol, timeframe)
            patterns['flags'] = await self.recognizer.detect_flags(symbol, timeframe)
            patterns['pennants'] = await self.recognizer.detect_pennants(symbol, timeframe)
            patterns['head_shoulders'] = await self.recognizer.detect_head_shoulders(symbol, timeframe)
            patterns['double_tops'] = await self.recognizer.detect_double_tops(symbol, timeframe)
            patterns['double_bottoms'] = await self.recognizer.detect_double_bottoms(symbol, timeframe)
            patterns['candlesticks'] = await self.recognizer.detect_candlestick_patterns(symbol, timeframe)
            
            # Perform comprehensive analysis
            comprehensive_analysis = await self.recognizer.analyze_comprehensive_patterns(symbol, timeframe)
            
            # ML-based pattern prediction
            ml_prediction = await self.recognizer.predict_pattern_ml(symbol, timeframe)
            
            # Generate trading signals
            signals = await self.recognizer.generate_pattern_signals(symbol, timeframe)
            
            result = {
                'symbol': symbol,
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat(),
                'trend_lines': trend_lines,
                'patterns': patterns,
                'comprehensive_analysis': comprehensive_analysis,
                'ml_prediction': ml_prediction,
                'signals': signals,
                'total_patterns': sum(len(pattern_list) for pattern_list in patterns.values()),
                'strongest_pattern': self.get_strongest_pattern(patterns),
                'confidence': ml_prediction.get('confidence', 0.0) if ml_prediction else 0.0
            }
            
            logger.info(f"Pattern recognition completed for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing patterns for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}
    
    def get_strongest_pattern(self, patterns: Dict) -> Optional[Dict]:
        """Get the strongest pattern from all detected patterns"""
        strongest = None
        max_strength = 0
        
        for pattern_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                strength = pattern.get('strength', 0)
                if strength > max_strength:
                    max_strength = strength
                    strongest = {
                        'type': pattern_type,
                        'strength': strength,
                        'details': pattern
                    }
        
        return strongest
    
    async def analyze_multiple_symbols(self, symbols: List[str], timeframe: str = 'H1') -> Dict:
        """Analyze patterns for multiple symbols"""
        logger.info(f"Analyzing patterns for {len(symbols)} symbols")
        
        tasks = [self.analyze_symbol(symbol, timeframe) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        
        return {
            'analysis_type': 'pattern_recognition',
            'symbols': symbols,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'summary': self.generate_summary(results)
        }
    
    def generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary of pattern recognition results"""
        summary = {
            'total_symbols': len(results),
            'symbols_with_patterns': 0,
            'total_patterns': 0,
            'pattern_breakdown': {
                'triangles': 0,
                'flags': 0,
                'pennants': 0,
                'head_shoulders': 0,
                'double_tops': 0,
                'double_bottoms': 0,
                'candlesticks': 0
            },
            'average_confidence': 0.0,
            'high_confidence_patterns': 0
        }
        
        total_confidence = 0
        valid_results = 0
        
        for result in results:
            if 'error' in result:
                continue
            
            patterns = result.get('patterns', {})
            total_patterns = result.get('total_patterns', 0)
            confidence = result.get('confidence', 0)
            
            if total_patterns > 0:
                summary['symbols_with_patterns'] += 1
                summary['total_patterns'] += total_patterns
                
                # Count patterns by type
                for pattern_type, pattern_list in patterns.items():
                    if pattern_type in summary['pattern_breakdown']:
                        summary['pattern_breakdown'][pattern_type] += len(pattern_list)
                
                # Confidence metrics
                total_confidence += confidence
                valid_results += 1
                
                if confidence >= 0.7:  # High confidence threshold
                    summary['high_confidence_patterns'] += 1
        
        if valid_results > 0:
            summary['average_confidence'] = total_confidence / valid_results
        
        return summary
    
    async def scan_for_pattern_opportunities(self, symbols: List[str], min_confidence: float = 0.7) -> Dict:
        """Scan for pattern-based trading opportunities"""
        logger.info(f"Scanning for pattern opportunities with min confidence {min_confidence}")
        
        # Analyze all symbols
        analysis_results = await self.analyze_multiple_symbols(symbols)
        
        # Filter high-confidence opportunities
        opportunities = []
        for result in analysis_results['results']:
            if 'error' in result:
                continue
            
            confidence = result.get('confidence', 0)
            signals = result.get('signals', [])
            
            if confidence >= min_confidence and signals:
                opportunities.append({
                    'symbol': result['symbol'],
                    'confidence': confidence,
                    'signals': signals,
                    'strongest_pattern': result.get('strongest_pattern'),
                    'total_patterns': result.get('total_patterns', 0)
                })
        
        # Sort by confidence
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'scan_type': 'pattern_opportunities',
            'min_confidence': min_confidence,
            'total_symbols': len(symbols),
            'opportunities_found': len(opportunities),
            'timestamp': datetime.now().isoformat(),
            'top_opportunities': opportunities[:10]  # Top 10 opportunities
        }
    
    def save_results(self, results: Dict, filename: str = None) -> str:
        """Save analysis results to file"""
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"reports/pattern_recognition_{timestamp}.json"
        
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
        print("PATTERN RECOGNITION RESULTS")
        print("="*60)
        print(f"Analysis Type: {results.get('analysis_type', 'N/A')}")
        print(f"Timeframe: {results.get('timeframe', 'N/A')}")
        print(f"Timestamp: {results.get('timestamp', 'N/A')}")
        print(f"Symbols Analyzed: {len(results.get('symbols', []))}")
        print("-"*60)
        
        # Print summary
        summary = results.get('summary', {})
        if summary:
            print(f"\n📈 SUMMARY:")
            print(f"   Total Patterns Found: {summary.get('total_patterns', 0)}")
            print(f"   Symbols with Patterns: {summary.get('symbols_with_patterns', 0)}")
            print(f"   Average Confidence: {summary.get('average_confidence', 0):.2%}")
            print(f"   High Confidence Patterns: {summary.get('high_confidence_patterns', 0)}")
            
            print(f"\n🔍 PATTERN BREAKDOWN:")
            for pattern_type, count in summary.get('pattern_breakdown', {}).items():
                if count > 0:
                    print(f"   {pattern_type.replace('_', ' ').title()}: {count}")
        
        # Print individual results
        for result in results.get('results', []):
            if 'error' in result:
                print(f"\n❌ {result['symbol']}: ERROR - {result['error']}")
                continue
            
            print(f"\n📊 {result['symbol']}:")
            print(f"   Total Patterns: {result['total_patterns']}")
            print(f"   Confidence: {result['confidence']:.2%}")
            
            if result['strongest_pattern']:
                strongest = result['strongest_pattern']
                print(f"   Strongest Pattern: {strongest['type'].replace('_', ' ').title()} (Strength: {strongest['strength']:.2f})")
            
            if result['signals']:
                for signal in result['signals']:
                    signal_type = signal.get('signal', 'N/A')
                    strength = signal.get('strength', 0)
                    print(f"   Signal: {signal_type} (Strength: {strength:.2f})")
        
        print("\n" + "="*60)
    
    async def run_analysis(self, symbols: List[str], timeframe: str = 'H1', 
                          save_results: bool = True, min_confidence: float = 0.0) -> Dict:
        """Run complete pattern recognition analysis"""
        logger.info(f"Starting pattern recognition for {symbols} on {timeframe}")
        
        # Run analysis
        results = await self.analyze_multiple_symbols(symbols, timeframe)
        
        # Scan for opportunities if confidence threshold is set
        if min_confidence > 0:
            opportunities = await self.scan_for_pattern_opportunities(symbols, min_confidence)
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
    parser = argparse.ArgumentParser(description='Advanced Pattern Recognition Runner')
    parser.add_argument('--symbols', nargs='+', default=['EURUSD', 'GBPUSD', 'USDJPY', 'BTCUSD', 'XAUUSD'],
                       help='Symbols to analyze')
    parser.add_argument('--timeframe', default='H1', help='Timeframe for analysis')
    parser.add_argument('--confidence', type=float, default=0.7, help='Minimum confidence for opportunities')
    parser.add_argument('--scan-opportunities', action='store_true', help='Scan for pattern opportunities')
    parser.add_argument('--train-model', action='store_true', help='Train ML model before analysis')
    parser.add_argument('--save', action='store_true', help='Save results to file')
    parser.add_argument('--output', help='Output filename for results')
    
    args = parser.parse_args()
    
    # Create runner
    runner = PatternRecognitionRunner()
    
    try:
        # Train model if requested
        if args.train_model:
            logger.info("Training ML pattern recognition model...")
            await runner.recognizer.train_ml_model()
        
        if args.scan_opportunities:
            # Scan for opportunities
            results = await runner.scan_for_pattern_opportunities(args.symbols, args.confidence)
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
        logger.info("Pattern recognition stopped by user")
    except Exception as e:
        logger.error(f"Pattern recognition error: {e}")
        sys.exit(1)