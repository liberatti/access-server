import { Injectable } from '@angular/core';
import { LocalStorageService } from './localstorage.service';
import * as moment from 'moment';

interface Abbreviations {
    [key: string]: number;
}

@Injectable({
    providedIn: 'root'
})
export abstract class FormaterService {

    constructor(private localstorage: LocalStorageService) { }

    byte(bytes: number, precision: number = 2): string {
        if (isNaN(parseFloat(String(bytes))) || !isFinite(bytes)) return 'N/A';

        const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
        const base = 1024;

        let i = 0;
        while (bytes >= base && i < sizes.length - 1) {
            bytes /= base;
            i++;
        }

        return bytes.toFixed(precision) + ' ' + sizes[i];
    }

    timestamp(value: Date, format: string = ''): string {
        if (value) {
            if (format==='') {
                let locale = this.localstorage.get("x-config").locale;
                format = locale.display.datetime;
            }
            return moment(value).format(format);
        }
        return value;
    }

    counter(value: number): string {
        if (isNaN(value) || !isFinite(value)) return 'N/A';

        const abs = Math.abs(value);
        const rounder = Math.pow(10, 2); // Alterado para 2 para dois dígitos após a vírgula
        const isNegative = value < 0;

        let key: string = '';
        let valueFormatted: string = '';

        const abbreviations: Abbreviations = {
            'K': 1e3,
            'M': 1e6,
            'B': 1e9,
            'T': 1e12,
        };

        for (const symbol in abbreviations) {
            if (abs >= abbreviations[symbol]) {
                key = symbol;
                valueFormatted = String((Math.round(value / abbreviations[symbol] * rounder) / rounder).toFixed(0));
            }
        }

        if (key === '') {
            valueFormatted = String((Math.round(value * rounder) / rounder).toFixed(0));
            return valueFormatted;
        } else {
            return (isNegative ? '-' : '') + valueFormatted + key;
        }
    }
    tpm(value: number): string {
        if (isNaN(value) || !isFinite(value)) return 'N/A';

        const abs = Math.abs(value);
        const rounder = Math.pow(10, 0); // Alterado para 2 para dois dígitos após a vírgula
        const isNegative = value < 0;

        let key: string = '';
        let valueFormatted: string = '';

        const abbreviations: Abbreviations = {
            'K tpm': 1e3,
            'M tpm': 1e6,
            'B tpm': 1e9,
            'T tpm': 1e12,
        };

        for (const symbol in abbreviations) {
            if (abs >= abbreviations[symbol]) {
                key = symbol;
                valueFormatted = String((Math.round(value / abbreviations[symbol] * rounder) / rounder).toFixed(0));
            }
        }

        if (key === '') {
            valueFormatted = String((Math.round(value * rounder) / rounder).toFixed(0));
            return valueFormatted;
        } else {
            return (isNegative ? '-' : '') + valueFormatted + key;
        }
    }

    time(value: number): string {
        if (isNaN(value) || !isFinite(value)) return 'N/A';

        const abs = Math.abs(value);
        const isNegative = value < 0;

        const timeUnits: { [key: string]: number } = {
            'ms': 1,
            's': 1000,
            'min': 60 * 1000,
            'h': 60 * 60 * 1000,
            'd': 24 * 60 * 60 * 1000,
        };

        let key = '';
        let valueFormatted = '';

        for (const unit in timeUnits) {
            if (abs >= timeUnits[unit]) {
                key = unit;
                valueFormatted = String((Math.round(value / timeUnits[unit]) * timeUnits[unit]).toFixed(2));
            }
        }
        if (key === '') {
            key = 'ms'
            valueFormatted = String(Math.trunc(value));
        }
        return (isNegative ? '-' : '') + valueFormatted + key;
    }
}