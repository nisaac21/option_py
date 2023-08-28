from abc import ABC, abstractmethod
import numpy as np
from typing import Sequence
import numbers 
from scipy.stats import gmean

from utils import validate_option_type
from quant_math import gbm_simulation

class PayOff(ABC):

    @abstractmethod
    def __init__(self, strike_price : float, option_type : str) -> None:
        validate_option_type(option_type)
        self.K = strike_price
        self.option_type = option_type

    @abstractmethod
    def pay_off(self, spot_prices : np.array) -> float:
        """Returns the pay off price at expiry for call option"""
        pass

class PayOffEuropean(PayOff):
    """Pay off for European call options"""

    def __init__(self, strike_price, option_type : str):
        super().__init__(strike_price, option_type)
    

    def pay_off(self, spot_prices: np.array) -> float:
        if self.option_type == 'call':
            return np.maximum(spot_prices[-1] - self.K, 0)
        elif self.option_type == 'put':
            return np.maximum(self.K - spot_prices[-1], 0)
        
    
class PayOffDigitalCall(PayOff):
    """Pay off for Digital """

    def __init__(self, strike_price : float, option_type : str, coupon : float):
        super().__init__(strike_price, option_type)
        self.C = coupon
    

    def pay_off(self, spot_prices: np.array) -> float:

        if self.option_type == 'call':
            if spot_prices[-1] <= self.K:
                return self.C
            else:
                return 0
        elif self.option_type == 'put':
            if spot_prices[-1] >= self.K:
                return self.C
            else:
                return 0

class PayOffDoubleDigital(PayOff):
    """Pay off for a Double Digital Option"""

    def __init__(self, upper_strike_price, lower_strike_price, coupon):
        self.U = upper_strike_price
        self.D = lower_strike_price
        self.C = coupon
    

    def pay_off(self, spot_prices: np.array) -> float:
        if spot_prices[-1] >= self.D and spot_prices <= self.U:
            return self.C
        else:
            return 0
        
class AsianOptionPayOff(PayOff):

    @abstractmethod
    def __init__(self, strike_price : float, option_type : str, path : np.array) -> None: 
        super().__init__(strike_price, option_type)

    @abstractmethod
    def _get_mean(self, path):
        pass

    @abstractmethod
    def pay_off(self, spot_prices : np.array) -> float:
        mean = self._get_mean(spot_prices)
        return PayOffEuropean(self.mean, self.option_type).pay_off(spot_prices[-1])

class AsianOptionArithmeticPayOff(AsianOptionPayOff):
    

    def __init__(self, strike_price : float, option_type : str, path : np.array) -> None:
        super().__init__(strike_price, option_type, path)

    def _get_mean(self, path):
        return np.mean(path)
    
class AsianOptionGeometricPayOff(AsianOptionPayOff):

    def __init__(self, strike_price : float, option_type : str) -> None:
        super().__init__(strike_price, option_type)

    def _get_mean(self, path) -> float:
        return gmean(path)