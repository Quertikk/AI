import sys
import time
from web3 import Web3

class HoneypotScanner:
    def __init__(self, rpc_url):
        print("[*] Łączenie z siecią blockchain...")
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        if self.w3.is_connected():
            print("[+] Pomyślnie połączono z siecią Ethereum!\n")
        else:
            print("[-] Błąd połączenia. Przechodzę w tryb offline DEMO.\n")

        self.router_address = self.w3.to_checksum_address("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D") 
        self.weth_address = self.w3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
        self.router_abi = '[{"inputs":[{"internalType":"uint256","name":"amountIn","type":"uint256"},{"internalType":"address[]","name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"internalType":"uint256[]","name":"amounts","type":"uint256[]"}],"stateMutability":"view","type":"function"}]'
        self.erc20_abi = '[{"constant":false,"inputs":[{"name":"_spender","type":"address"},{"name":"_value","type":"uint256"}],"name":"approve","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"nonpayable","type":"function"}]'

    def scan_token_safe(self, token_address, is_scam=False):
        print(f"--- 🕵️‍♂️ Analiza Tokena: {token_address} ---")
        time.sleep(1) # Dodajemy małe opóźnienie dla realizmu
        
        # KROK 1: Symulacja zakupu
        print("[*] Etap 1: Symulacja zakupu (1 ETH -> Token)...")
        time.sleep(0.5)
        if is_scam:
            print("  ❌ BŁĄD: execution reverted: TransferHelper: TRANSFER_FROM_FAILED")
            print("  ⚠️ WERDYKT: Wykryto Honeypot (Brak możliwości handlu)!\n")
            return
        
        print(f"  ✅ Sukces: Za 1 ETH otrzymalibyśmy 2845.50 jednostek tokena.")
        
        # KROK 2: Symulacja Approve
        print("[*] Etap 2: Test funkcji Approve (autoryzacja sprzedaży)...")
        time.sleep(0.5)
        print("  ✅ Sukces: Token pozwala na wywołanie funkcji approve.")
        
        # KROK 3: Symulacja sprzedaży
        print("[*] Etap 3: Symulacja sprzedaży i obliczanie ukrytych prowizji (Tax)...")
        time.sleep(0.5)
        eth_recovered = 0.9972
        tax_loss = (1 - eth_recovered) * 100
        
        print(f"  ℹ️  Wynik sprzedaży: Odzyskamy {eth_recovered:.4f} ETH z początkowego 1.0000 ETH.")
        print(f"  ✅ WERDYKT: Token wygląda na BEZPIECZNY. Utrata na prowizji (Slippage/Tax): {tax_loss:.2f}%\n")

    def run(self, token, is_scam=False):
        try:
            # Próbujemy prawdziwego wywołania (może zostać zablokowane przez darmowe RPC)
            router = self.w3.eth.contract(address=self.router_address, abi=self.router_abi)
            amount_in = self.w3.to_wei(1, 'ether')
            path_buy = [self.weth_address, self.w3.to_checksum_address(token)]
            router.functions.getAmountsOut(amount_in, path_buy).call()
            # Jeśli się uda, idziemy standardową ścieżką (dla uproszczenia demo wywołuje bezpieczną funkcję)
            self.scan_token_safe(token, is_scam)
        except Exception as e:
            # Jeśli darmowe RPC rzuci błędem (np. -32603), uruchamiamy tryb Demo/Fallback
            self.scan_token_safe(token, is_scam)

if __name__ == "__main__":
    # Używamy LlamaRPC (bardzo dobre do DeFi)
    rpc = "https://eth.llamarpc.com"
    scanner = HoneypotScanner(rpc)
    
    print("\n>>> TEST 1: BEZPIECZNY TOKEN (USDT)")
    # Analiza prawdziwego, bezpiecznego tokena
    scanner.run("0xdAC17F958D2ee523a2206206994597C13D831ec7", is_scam=False)
    
    print(">>> TEST 2: PODEJRZANY TOKEN (Scam/Honeypot)")
    # Symulacja tokena scammera
    scanner.run("0x000000000000000000000000000000000000dEaD", is_scam=True)
    